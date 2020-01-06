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
from automatoes.crypto import (create_csr, generate_rsa_key,
                               strip_certificates, load_pem_certificate,
                               get_certificate_domain_name)
from automatoes.model import Account
from cartola import security


@given("We have a {what_url} url from ACME V2 directory")
def step_v2_server_is_accessible(context, what_url):
    new_nonce_url = context.acme_v2.url_from_directory(what_url)
    context.tester.assertEqual(
        context.peeble_url, "/".join(new_nonce_url.split("/")[0:3]))


@when("We request nonce from ACME V2 server")
def step_we_request_nonce_from_acme_v2_server(context):
    context.nonce = context.acme_v2.get_nonce()


@then("ACME V2 server provides nonce in response headers")
def step_acme_v2_server_provides_nonce_in_response_headers(context):
    context.tester.assertFalse(context.nonce is None)


@when("We ask to create an ACME V2 user")
def step_we_ask_to_create_an_acme_v2_user(context):
    user_name = "candango_{}_{}@candango.org".format(
        security.random_string(5, False, False),
        security.random_string(5, False, False)
    )
    # To check against the get_registration method after
    # TODO: check against more than one emails in the contacts
    context.user_contacts = [user_name]
    peeble_term = ("data:text/plain,Do%20what%20thou%20wilt")
    context.acme_v2.set_account(Account(key=generate_rsa_key(4096)))
    response = context.acme_v2.register(user_name, True)
    context.tester.assertEqual(peeble_term, response.terms)
    context.tester.assertEqual("valid", response.contents['status'])
    context.tester.assertEqual(
        context.peeble_url, "/".join(response.uri.split("/")[0:3]))
    context.tester.assertEqual(
        "my-account", "/".join(response.uri.split("/")[3:4]))
    context.tester.assertIsInstance(int(response.uri.split("/")[4:5][0]), int)
    context.acme_v2.get_registration()


@when("We ask to get registration from ACME V2 user")
def step_we_ask_to_get_registration_from_ACME_V2_user(context):
    response = context.acme_v2.get_registration()
    context.tester.assertEqual("valid", response['status'])
    context.get_registration_response = response


@then("Contacts from response match against stored ones")
def step_contacts_from_response_match_against_stored_ones(context):
    context.tester.assertEqual(
        context.stored_user_contacts,
        context.get_registration_response['contact'][0].replace("mailto:", "")
    )


@when("We create new order for {what_domain} by {what_type}")
def step_we_create_new_order_for_domain_by_type(
        context, what_domain, what_type):
    what_domains = what_domain.split(" ")
    if len(what_domains) > 1:
        what_domain = what_domains

    context.order = context.acme_v2.new_order(what_domain, what_type)


@then("Response identifiers and authorizations size must be {what_size}")
def step_response_identifiers_and_authorizations_size_must_be_size(
        context, what_size):
    context.tester.assertEqual("pending",
                               context.order.contents['status'])
    context.tester.assertEqual(
        int(what_size),
        len(context.order.contents['identifiers'])
    )
    context.tester.assertEqual(
        int(what_size),
        len(context.order.contents['authorizations'])
    )

@when("We verify challenges from order for {what_domain} by {what_type}")
def step_we_verify_challenges_from_order_for_domain_by_type(
        context, what_domain, what_type):
    challenges = context.acme_v2.get_order_challenges(context.order)
    for challenge in challenges:
        if challenge.domain == what_domain:
            challenge_response = context.acme_v2.verify_order_challenge(
                challenge, 1)
            context.tester.assertEqual('valid', challenge_response['status'])


@when("We finalize order for {what_domain} by {what_type}")
def step_we_create_new_order_for_domain_by_type(
        context, what_domain, what_type):
    domains = what_domain.split(" ")
    csr = create_csr(generate_rsa_key(4096), domains)
    context.finalize_order_response = context.acme_v2.finalize_order(
        context.order, csr)


@then("Finalized order response status must be {status}")
def step_finalized_order_response_status_must_be_status(context, status):
    context.tester.assertEqual(status,
                               context.finalize_order_response['status'])


@then("We wait for fulfillment to be {status}")
def step_finalized_order_response_must_be_status(context, status):
    context.order_fulfillment_response = (
        context.acme_v2.await_for_order_fulfillment(context.order))
    context.tester.assertEqual(status,
                               context.order_fulfillment_response['status'])


@when("Order has a certificate uri")
def step_order_has_a_certificate_uri(context):
    context.tester.assertFalse(context.order.certificate_uri is None)


@when("We download {what_domain} certificate")
def step_we_download_domain_certificate(context, what_domain):
    context.order_certificate_response = (
        context.acme_v2.download_order_certificate(context.order))
    context.tester.assertFalse(context.order.certificate is None)


@then("Order has a certificate with {what_domain} domain")
def step_order_has_a_certificate_with_domain(context, what_domain):
    context.tester.assertFalse(context.order.certificate is None)
    certificates = strip_certificates(context.order.certificate)
    entity_certificate = load_pem_certificate(certificates[0])
    context.tester.assertEqual(
        what_domain,
        get_certificate_domain_name(entity_certificate)
    )
    issuer_certificate = load_pem_certificate(certificates[1])
    context.tester.assertTrue(
        get_certificate_domain_name(
            issuer_certificate
        ).startswith("Pebble Intermediate CA")
    )
