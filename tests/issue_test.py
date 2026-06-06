#!/usr/bin/env python
#
# Copyright 2019-2025 Flavio Garcia
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

import unittest
from cryptography import x509
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa
import datetime
from io import BytesIO
import warnings

from automatoes.crypto import export_pem_certificate
from automatoes.issue import EXPIRATION_FORMAT, write_certificates


def create_test_certificate(common_name):
    """Create a self-signed certificate for issue unit tests."""
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )
    subject = issuer = x509.Name(
        [
            x509.NameAttribute(x509.NameOID.COUNTRY_NAME, "US"),
            x509.NameAttribute(x509.NameOID.COMMON_NAME, common_name),
        ]
    )
    now = datetime.datetime.now(datetime.timezone.utc)
    return (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(private_key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now)
        .not_valid_after(now + datetime.timedelta(days=30))
        .sign(private_key, hashes.SHA256())
    )


class IssueTestCase(unittest.TestCase):
    def test_write_certificates_writes_all_pem_blocks(self):
        certificates = [
            export_pem_certificate(create_test_certificate("leaf.test")),
            export_pem_certificate(create_test_certificate("intermediate-1")),
            export_pem_certificate(create_test_certificate("intermediate-2")),
        ]
        chain_output = BytesIO()
        intermediate_output = BytesIO()

        write_certificates(chain_output, certificates)
        write_certificates(intermediate_output, certificates[1:])

        self.assertEqual(
            3,
            chain_output.getvalue().count(b"-----BEGIN CERTIFICATE-----"),
        )
        self.assertEqual(
            2,
            intermediate_output.getvalue().count(
                b"-----BEGIN CERTIFICATE-----",
            ),
        )

    def test_certificate_expiration_uses_utc_property(self):
        """Test that certificate expiration formatting uses
        not_valid_after_utc."""
        # Generate a test certificate
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
        )

        subject = issuer = x509.Name(
            [
                x509.NameAttribute(x509.NameOID.COUNTRY_NAME, "US"),
                x509.NameAttribute(
                    x509.NameOID.COMMON_NAME,
                    "test.example.com",
                ),
            ]
        )

        next_year = datetime.datetime.now(datetime.timezone.utc).year + 1
        # Create expiration date in UTC
        expiration_date = datetime.datetime(
            next_year, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc
        )

        cert = (
            x509.CertificateBuilder()
            .subject_name(subject)
            .issuer_name(issuer)
            .public_key(private_key.public_key())
            .serial_number(x509.random_serial_number())
            .not_valid_before(datetime.datetime.now())
            .not_valid_after(expiration_date)
            .sign(private_key, hashes.SHA256())
        )

        # Test that not_valid_after_utc returns UTC-aware datetime
        self.assertIsNotNone(cert.not_valid_after_utc)
        self.assertIsNotNone(cert.not_valid_after_utc.tzinfo)

        # Test that formatting works correctly with not_valid_after_utc
        formatted_expiration = cert.not_valid_after_utc.strftime(
            EXPIRATION_FORMAT,
        )
        self.assertEqual(formatted_expiration, f"{next_year}-12-31")

        # Test that not_valid_after (deprecated) produces warnings
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            _ = cert.not_valid_after
            # Check that a deprecation warning was issued
            self.assertTrue(len(w) > 0)
            deprecation_warning_found = any(
                "deprecated" in str(warning.message).lower() for warning in w
            )
            self.assertTrue(deprecation_warning_found)
