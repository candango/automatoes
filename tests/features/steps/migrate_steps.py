# Copyright 2019-2023 Flávio Gonçalves Garcia
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

from automatoes.crypto import (certbot_key_data_to_int,
                               generate_rsa_key_from_parameters)
from automatoes.acme import AcmeV2
from automatoes.model import Account
import base64
from behave import given, when, then
import binascii
from cartola import fs
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey
import json
import os
from tests.features.steps.environment_steps import (create_file,
                                                    get_absolute_path)


def key_int_to_data(value: int) -> str:
    """ This is the invertion of what happens inside
    automatoes.crypto.certbot_key_data_to_int
    """
    hex_value = hex(value).replace("0x", "")
    if len(hex_value) % 2:
        hex_value = "0%s" % hex_value
    return base64.b64encode(
        binascii.unhexlify(hex_value), b"-_"
    ).replace(b"=", b"").decode()


@given("A certbot account is located at {certbot_path} path")
def certbot_account_located_at(context, certbot_path):
    certbot_path = get_absolute_path(certbot_path)

    context.tester.assertTrue(os.path.exists(certbot_path))
    meta_path = os.path.join(certbot_path, "meta.json")
    key_path = os.path.join(certbot_path, "private_key.json")
    regr_path = os.path.join(certbot_path, "regr.json")
    context.tester.assertTrue(os.path.isfile(meta_path))
    context.tester.assertTrue(os.path.isfile(key_path))
    context.tester.assertTrue(os.path.isfile(regr_path))

    context.meta_data = json.loads(fs.read(meta_path))
    context.key_data = json.loads(fs.read(key_path))
    context.regr_data = json.loads(fs.read(regr_path))


@when("A RSA key is converted from the key data file parameter")
def rsa_key_converted_from_key_data(context):
    key_data_int = certbot_key_data_to_int(context.key_data)
    context.private_key = generate_rsa_key_from_parameters(
        key_data_int['p'], key_data_int['q'], key_data_int['d'],
        key_data_int['dp'], key_data_int['dq'], key_data_int['qi'],
        key_data_int['e'], key_data_int['n']
    )
    context.tester.assertTrue(isinstance(context.private_key, RSAPrivateKey))


@when("An automatoes account is created")
def automatoes_account_created(context):
    account = Account(key=context.private_key, uri=context.regr_data['uri'])
    context.acme_v2.set_account(account)


@then("Convert account to certbot format")
def convert_account_to_certbot_format(context):
    key: RSAPrivateKey = context.acme_v2.account.key

    sandbox_path = os.path.join(os.getcwd(), "tests", "features", "sandbox")
    key_path = os.path.join(sandbox_path, "private_key.json")
    meta_path = os.path.join(sandbox_path, "meta.json")
    regr_path = os.path.join(sandbox_path, "regr.json")

    key_data = {
        'p': key_int_to_data(key.private_numbers().p),
        'q': key_int_to_data(key.private_numbers().q),
        'd': key_int_to_data(key.private_numbers().d),
        'dp': key_int_to_data(key.private_numbers().dmp1),
        'dq': key_int_to_data(key.private_numbers().dmq1),
        'qi': key_int_to_data(key.private_numbers().iqmp),
        'e': key_int_to_data(key.public_key().public_numbers().e),
        'n': key_int_to_data(key.public_key().public_numbers().n)
    }

    meta_data = {
        'creation_dt': "2023-01-08T19:32:30Z",
        'creation_host': "any-host",
        'register_to_eff': ",".join(context.user_contacts)
    }

    acme_v2: AcmeV2 = context.acme_v2

    regr_data = {
        'body': {},
        'uri': acme_v2.account.uri
    }

    real_key_path = create_file(key_path, json.dumps(key_data))
    context.tester.assertTrue(os.path.isfile(real_key_path))
    real_meta_path = create_file(meta_path, json.dumps(meta_data))
    context.tester.assertTrue(os.path.isfile(real_meta_path))
    real_regr_path = create_file(regr_path, json.dumps(regr_data))
    context.tester.assertTrue(os.path.isfile(real_regr_path))
