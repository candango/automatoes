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

from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from unittest import TestCase
from unittest.mock import Mock, patch
import hashlib
import os
import tempfile

from cryptography import x509
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa

from automatoes.crypto import export_pem_certificate, export_private_key
from automatoes.errors import AutomatoesError
from automatoes.issue import issue
from automatoes.model import Order


class IssueTestCase(TestCase):
    def test_valid_order_without_key_fails_before_download(self):
        certificate_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
        )
        now = datetime.now(timezone.utc)
        certificate = (
            x509.CertificateBuilder()
            .subject_name(x509.Name([
                x509.NameAttribute(
                    x509.NameOID.COMMON_NAME,
                    "issue-regression.candango.org",
                ),
            ]))
            .issuer_name(x509.Name([
                x509.NameAttribute(
                    x509.NameOID.COMMON_NAME,
                    "issue-regression.candango.org",
                ),
            ]))
            .public_key(certificate_key.public_key())
            .serial_number(x509.random_serial_number())
            .not_valid_before(now)
            .not_valid_after(now + timedelta(days=30))
            .sign(certificate_key, hashes.SHA256())
        )
        fake_acme = Mock()
        fake_acme.download_order_certificate.return_value = SimpleNamespace(
            content=export_pem_certificate(certificate),
        )

        with tempfile.TemporaryDirectory() as root:
            domains = ["issue-regression.candango.org"]
            orders_path = os.path.join(root, "orders")
            order_hash = hashlib.sha256(
                "_".join(domains).encode("ascii"),
            ).hexdigest()
            order_path = os.path.join(orders_path, order_hash)
            os.makedirs(order_path)
            order_file = os.path.join(order_path, "order.json")
            order = Order(
                contents={"status": "valid"},
                uri="https://acme.test/order/1",
                ty_pe="dns",
            )
            order.certificate_uri = "https://acme.test/certificate/1"
            with open(order_file, "wb") as order_handle:
                order_handle.write(order.serialize())

            with patch("automatoes.issue.AcmeV2", return_value=fake_acme):
                with self.assertRaises(AutomatoesError):
                    issue(
                        "https://acme.test",
                        {"current": root, "orders": orders_path},
                        account=None,
                        domains=domains,
                        key_size=2048,
                        output_path=os.path.join(root, "output"),
                    )

        fake_acme.download_order_certificate.assert_not_called()

    def test_existing_order_rejects_wrong_key_file(self):
        certificate_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
        )
        wrong_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
        )
        now = datetime.now(timezone.utc)
        certificate = (
            x509.CertificateBuilder()
            .subject_name(x509.Name([
                x509.NameAttribute(
                    x509.NameOID.COMMON_NAME,
                    "issue-regression.candango.org",
                ),
            ]))
            .issuer_name(x509.Name([
                x509.NameAttribute(
                    x509.NameOID.COMMON_NAME,
                    "issue-regression.candango.org",
                ),
            ]))
            .public_key(certificate_key.public_key())
            .serial_number(x509.random_serial_number())
            .not_valid_before(now)
            .not_valid_after(now + timedelta(days=30))
            .sign(certificate_key, hashes.SHA256())
        )
        fake_acme = Mock()
        fake_acme.download_order_certificate.return_value = SimpleNamespace(
            content=export_pem_certificate(certificate),
        )

        with tempfile.TemporaryDirectory() as root:
            domains = ["issue-regression.candango.org"]
            orders_path = os.path.join(root, "orders")
            order_hash = hashlib.sha256(
                "_".join(domains).encode("ascii"),
            ).hexdigest()
            order_path = os.path.join(orders_path, order_hash)
            os.makedirs(order_path)
            order_file = os.path.join(order_path, "order.json")
            order = Order(
                contents={"status": "valid"},
                uri="https://acme.test/order/1",
                ty_pe="dns",
            )
            order.certificate_uri = "https://acme.test/certificate/1"
            with open(order_file, "wb") as order_handle:
                order_handle.write(order.serialize())
            with open(order_file, "rb") as order_handle:
                original_order = order_handle.read()

            key_file = os.path.join(root, "wrong.pem")
            with open(key_file, "wb") as key_handle:
                key_handle.write(export_private_key(wrong_key))

            output_path = os.path.join(root, "output")
            with patch("automatoes.issue.AcmeV2", return_value=fake_acme):
                with self.assertRaisesRegex(
                    AutomatoesError,
                    "does not match the certificate",
                ):
                    issue(
                        "https://acme.test",
                        {"current": root, "orders": orders_path},
                        account=None,
                        domains=domains,
                        key_size=2048,
                        key_file=key_file,
                        output_path=output_path,
                    )

            with open(order_file, "rb") as saved_order_file:
                saved_order = Order.deserialize(saved_order_file.read())
            self.assertIsNone(saved_order.key)
            with open(order_file, "rb") as order_handle:
                self.assertEqual(original_order, order_handle.read())
            self.assertFalse(os.path.exists(output_path))

        fake_acme.download_order_certificate.assert_called_once()
