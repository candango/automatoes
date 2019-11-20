#!/usr/bin/env python
#
# Copyright 2019 Flavio Garcia
# Copyright 2016-2017 Veeti Paananen under MIT License
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

from behave import given, when, then
from automatoes.account import Account
from automatoes.crypto import generate_rsa_key


@given("We have a {what_url} url from ACME V2 directory")
def step_v2_server_is_accessible(context, what_url):
    new_nounce_url = context.acme_v2.url_from_directory(what_url)
    context.tester.assertEqual(
        context.peeble_url, "/".join(new_nounce_url.split("/")[0:3]))


@when("We request nounce from ACME V2 server")
def step_we_request_nounce_from_acme_v2_server(context):
    context.nounce = context.acme_v2.get_nonce()


@then("ACME V2 server provides nounce in response headers")
def step_acme_v2_server_provides_nounce_in_response_headers(context):
    context.tester.assertFalse(context.nounce is None)

@when("We ask to create an ACME V2 user")
def step_we_ask_to_create_an_ACME_V2_user(context):
    user_name = "candango_{}_{}@candango.org".format(
        context.random_string(5, False, False),
        context.random_string(5, False, False)
    )
    peeble_term = ("data:text/plain,Do%20what%20thou%20wilt")
    context.acme_v2.set_account(Account(key=generate_rsa_key(4096)))
    response = context.acme_v2.register(user_name)
    context.tester.assertEqual(peeble_term, response.terms)
    context.tester.assertEqual("valid", response.contents['status'])
    context.tester.assertEqual(
        context.peeble_url, "/".join(response.uri.split("/")[0:3]))
    context.tester.assertEqual(
        "my-account", "/".join(response.uri.split("/")[3:4]))
    context.tester.assertIsInstance(int(response.uri.split("/")[4:5][0]), int)
