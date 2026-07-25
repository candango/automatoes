# Copyright 2019-2025 Flavio Garcia
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.

import base64
import json
import os
import tempfile
import unittest
from unittest.mock import patch

from automatoes.acme import AcmeV2
from automatoes.crypto import (
    certbot_key_data_to_int,
    generate_rsa_key_from_parameters,
    create_csr,
    generate_rsa_key,
    get_certificate_domain_name,
    get_issuer_certificate_domain_name,
    load_pem_certificate,
    strip_certificates,
)
from automatoes.migrate import migrate
from automatoes.model import Account, Order
from automatoes.protocol import AcmeRequestsTransport, AcmeV2Pesant
from cartola import fs



def get_absolute_path(directory):
    return os.path.realpath(
        os.path.join(os.path.dirname(__file__), directory)
    )

PEBBLE_URL = "https://localhost:14000"
PEBBLE_CERTIFICATE = get_absolute_path("certs/candango.minica.pem")
TERMS_URL = "data:text/plain,Do%20what%20thou%20wilt"


def certbot_key_data_for(key):
    numbers = key.private_numbers()
    public_numbers = numbers.public_numbers

    def encode(value):
        raw = value.to_bytes((value.bit_length() + 7) // 8, "big")
        return base64.urlsafe_b64encode(raw).decode().rstrip("=")

    return {
        "p": encode(numbers.p),
        "q": encode(numbers.q),
        "d": encode(numbers.d),
        "dp": encode(numbers.dmp1),
        "dq": encode(numbers.dmq1),
        "qi": encode(numbers.iqmp),
        "e": encode(public_numbers.e),
        "n": encode(public_numbers.n),
    }


class AcmeIntegrationTestCase(unittest.TestCase):
    """Base case for tests that require a running Pebble server."""

    def setUp(self):
        self.acme_v2 = AcmeV2(
            PEBBLE_URL,
            None,
            directory="dir",
            verify=PEBBLE_CERTIFICATE,
        )

    def register_account(self):
        email = f"candango_{os.getpid()}_{id(self)}@candango.org"
        self.acme_v2.set_account(Account(key=generate_rsa_key(4096)))
        response = self.acme_v2.register(email, True)
        self.assertEqual(TERMS_URL, response.terms)
        self.assertEqual("valid", response.contents["status"])
        self.assertTrue(response.uri.startswith(PEBBLE_URL))
        return email

    def issue_certificate(self, domains, challenge_type="dns"):
        if isinstance(domains, str):
            domains = [domains]

        order = self.acme_v2.new_order(domains, challenge_type)
        self.assertEqual("pending", order.contents["status"])
        self.assertEqual(len(domains), len(order.contents["identifiers"]))
        self.assertEqual(len(domains), len(order.contents["authorizations"]))

        challenges = self.acme_v2.get_order_challenges(order)
        for challenge in challenges:
            response = self.acme_v2.verify_order_challenge(challenge, 1)
            self.assertEqual("valid", response["status"])

        csr = create_csr(generate_rsa_key(4096), domains)
        response = self.acme_v2.finalize_order(order, csr)
        self.assertEqual("processing", response["status"])

        response = self.acme_v2.await_for_order_fulfillment(order)
        self.assertEqual("valid", response["status"])
        self.assertIsNotNone(order.certificate_uri)

        self.acme_v2.download_order_certificate(order)
        self.assertIsNotNone(order.certificate)
        return order

    def assert_certificate_domain(self, certificate, expected_domain):
        certificates = strip_certificates(certificate)
        entity_certificate = load_pem_certificate(certificates[0])
        issuer_certificate = load_pem_certificate(certificates[1])
        self.assertEqual(
            expected_domain,
            get_certificate_domain_name(entity_certificate),
        )
        self.assertTrue(
            get_issuer_certificate_domain_name(issuer_certificate).startswith(
                "Pebble Intermediate CA"
            )
        )


class AcmeProtocolIntegrationTestCase(AcmeIntegrationTestCase):
    def test_nonce_from_directory(self):
        transport = AcmeRequestsTransport(PEBBLE_URL)
        protocol = AcmeV2Pesant(
            transport,
            url=PEBBLE_URL,
            directory="dir",
            verify=PEBBLE_CERTIFICATE,
        )
        directory_url = protocol.directory()["newNonce"]
        self.assertEqual(PEBBLE_URL, "/".join(directory_url.split("/")[:3]))
        self.assertIsNotNone(self.acme_v2.get_nonce())

    def test_register_and_read_account(self):
        email = self.register_account()
        response = self.acme_v2.get_registration()
        self.assertEqual("valid", response["status"])
        self.assertEqual(f"mailto:{email}", response["contact"][0])


class AcmeCertificateIntegrationTestCase(AcmeIntegrationTestCase):
    def setUp(self):
        super().setUp()
        self.register_account()

    def test_issue_dns_certificate(self):
        order = self.issue_certificate("testdns.candango.org")
        self.assert_certificate_domain(
            order.certificate,
            "testdns.candango.org",
        )

        with tempfile.TemporaryDirectory() as directory:
            order_path = os.path.join(directory, "order.json")
            certificate_path = os.path.join(directory, "certificate.pem")
            fs.write(order_path, order.serialize(), True)
            restored_order = Order.deserialize(fs.read(order_path, True))
            self.assertEqual(order.uri, restored_order.uri)
            self.assertEqual(order.type, restored_order.type)
            self.assertEqual(
                order.certificate_uri,
                restored_order.certificate_uri,
            )

            self.acme_v2.download_order_certificate(restored_order)
            fs.write(certificate_path, restored_order.certificate, True)
            self.assertTrue(os.path.isfile(order_path))
            self.assertTrue(os.path.isfile(certificate_path))

            os.remove(order_path)
            os.remove(certificate_path)
            self.assertFalse(os.path.exists(order_path))
            self.assertFalse(os.path.exists(certificate_path))

    def test_issue_http_certificate(self):
        order = self.issue_certificate("testhttp.candango.org", "http")
        self.assert_certificate_domain(
            order.certificate,
            "testhttp.candango.org",
        )

    def test_issue_multiple_domain_certificate(self):
        domains = ["testmulti1.candango.org", "testmulti2.candango.org"]
        order = self.issue_certificate(domains)
        self.assert_certificate_domain(
            order.certificate,
            "testmulti1.candango.org",
        )

    def test_issue_wildcard_certificate(self):
        order = self.issue_certificate("*.candango.org")
        self.assert_certificate_domain(order.certificate, "*.candango.org")

    def test_revoke_certificate(self):
        order = self.issue_certificate("valid.candango.org")
        certificate_pem = strip_certificates(order.certificate)[0]
        certificate = load_pem_certificate(certificate_pem)
        response = self.acme_v2.revoke_certificate(certificate)
        self.assertEqual(200, response.status_code)


class AccountMigrationTestCase(unittest.TestCase):
    def test_certbot_key_data_can_restore_account_key(self):
        key = generate_rsa_key(2048)
        numbers = key.private_numbers()
        parameters = certbot_key_data_to_int(certbot_key_data_for(key))
        restored = generate_rsa_key_from_parameters(
            parameters["p"],
            parameters["q"],
            parameters["d"],
            parameters["dp"],
            parameters["dq"],
            parameters["qi"],
            parameters["e"],
            parameters["n"],
        )

        self.assertEqual(numbers.d, restored.private_numbers().d)

    def test_migrate_writes_account_from_certbot_files(self):
        key = generate_rsa_key(2048)
        with tempfile.TemporaryDirectory() as directory:
            certbot_path = os.path.join(directory, "certbot")
            os.mkdir(certbot_path)
            fs.write(
                os.path.join(certbot_path, "private_key.json"),
                json.dumps(certbot_key_data_for(key)),
            )
            fs.write(
                os.path.join(certbot_path, "regr.json"),
                json.dumps({"uri": "https://example.test/acme/acct/1"}),
            )
            account_path = os.path.join(directory, "account.json")

            with patch("automatoes.migrate.confirm", return_value=True):
                migrate(account_path, certbot_path)

            account = Account.deserialize(fs.read(account_path))

        self.assertEqual("https://example.test/acme/acct/1", account.uri)
        self.assertEqual(
            key.private_numbers().d,
            account.key.private_numbers().d,
        )

    def test_account_and_contacts_files_round_trip(self):
        account = Account(
            key=generate_rsa_key(2048),
            uri="https://example.test",
        )
        contacts = "admin@example.test"
        with tempfile.TemporaryDirectory() as directory:
            account_path = os.path.join(directory, "account.json")
            contacts_path = os.path.join(directory, "user_contacts.txt")
            fs.write(account_path, account.serialize(), True)
            fs.write(contacts_path, contacts)

            restored = Account.deserialize(fs.read(account_path))
            restored_contacts = fs.read(contacts_path)

        self.assertEqual(account.uri, restored.uri)
        self.assertEqual(contacts, restored_contacts)

    def test_account_can_be_serialized_and_restored(self):
        account = Account(
            key=generate_rsa_key(2048),
            uri="https://example.test",
        )
        with tempfile.TemporaryDirectory() as directory:
            path = os.path.join(directory, "account.json")
            fs.write(path, account.serialize(), True)
            restored = Account.deserialize(fs.read(path))

        self.assertEqual(account.uri, restored.uri)
        self.assertEqual(
            account.key.private_numbers().d,
            restored.key.private_numbers().d,
        )
