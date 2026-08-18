# Copyright 2026 Flavio Garcia
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import hashlib
import os
import shutil
import tempfile

from behave import given, then, when
from automatoes import issue as issue_command
from automatoes.acme import AcmeV2
from automatoes.crypto import create_csr, generate_rsa_key
from automatoes.errors import AutomatoesError
from automatoes.model import Account
from cartola import fs, security


PEBBLE_URL = "https://localhost:14000"
DOMAIN = "issue-regression.candango.org"


@given("A valid Pebble order was finalized with a private key")
def valid_pebble_order_was_finalized(context):
    account = Account(key=generate_rsa_key(2048))
    acme = AcmeV2(
        PEBBLE_URL,
        account,
        directory="dir",
        verify="tests/certs/candango.minica.pem",
    )
    email = "issue_{}_{}@candango.org".format(
        security.random_string(5, False, False),
        security.random_string(5, False, False),
    )
    acme.register(email, True)

    order = acme.new_order(DOMAIN, "dns")
    for challenge in acme.get_order_challenges(order):
        acme.verify_order_challenge(challenge, timeout=1, retry_limit=1)

    certificate_key = generate_rsa_key(2048)
    final_order = acme.finalize_order(
        order,
        create_csr(certificate_key, [DOMAIN]),
    )
    order.contents = final_order
    context.tester.assertIn(final_order["status"], ["processing", "valid"])

    fulfillment = acme.await_for_order_fulfillment(
        order,
        timeout=1,
        iterations=5,
    )
    order.contents = fulfillment
    context.tester.assertEqual("valid", fulfillment["status"])
    context.tester.assertIsNotNone(order.certificate_uri)

    # Simulate an old order.json that has the certificate URI but no key.
    order.key = None
    context.issue_account = account
    context.issue_order = order


@when("Automatoes issues the valid order without the local private key")
def automatoes_issues_order_without_local_key(context):
    root = tempfile.mkdtemp(prefix="automatoes-issue-")
    orders_path = os.path.join(root, "orders")
    order_hash = hashlib.sha256(DOMAIN.encode("ascii")).hexdigest()
    order_path = os.path.join(orders_path, order_hash)
    os.makedirs(order_path)
    order_file = os.path.join(order_path, "order.json")
    fs.write(order_file, context.issue_order.serialize(), binary=True)

    output_path = os.path.join(root, "output")
    try:
        issue_command.issue(
            PEBBLE_URL,
            {"current": root, "orders": orders_path},
            context.issue_account,
            [DOMAIN],
            key_size=2048,
            output_path=output_path,
            output_filename="issue-regression",
        )
    except AutomatoesError as error:
        context.issue_error = error
    else:
        context.issue_error = None
    context.issue_output_path = output_path
    context.issue_root = root


@then("The valid order is rejected without its private key")
def valid_order_is_rejected_without_private_key(context):
    try:
        context.tester.assertIsNotNone(context.issue_error)
        context.tester.assertIn(
            "without its private key",
            str(context.issue_error),
        )
        context.tester.assertFalse(os.path.exists(context.issue_output_path))
    finally:
        shutil.rmtree(context.issue_root)
