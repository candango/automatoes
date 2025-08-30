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
import warnings

from automatoes.issue import EXPIRATION_FORMAT


class IssueTestCase(unittest.TestCase):

    def test_certificate_expiration_uses_utc_property(self):
        """Test that certificate expiration formatting uses
        not_valid_after_utc."""
        # Generate a test certificate
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
        )

        subject = issuer = x509.Name([
            x509.NameAttribute(x509.NameOID.COUNTRY_NAME, 'US'),
            x509.NameAttribute(x509.NameOID.COMMON_NAME, 'test.example.com'),
        ])

        # Create expiration date in UTC
        expiration_date = datetime.datetime(
                2025, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc)

        cert = x509.CertificateBuilder().subject_name(
            subject
        ).issuer_name(
            issuer
        ).public_key(
            private_key.public_key()
        ).serial_number(
            x509.random_serial_number()
        ).not_valid_before(
            datetime.datetime.now()
        ).not_valid_after(
            expiration_date
        ).sign(private_key, hashes.SHA256())

        # Test that not_valid_after_utc returns UTC-aware datetime
        self.assertIsNotNone(cert.not_valid_after_utc)
        self.assertIsNotNone(cert.not_valid_after_utc.tzinfo)

        # Test that formatting works correctly with not_valid_after_utc
        formatted_expiration = cert.not_valid_after_utc.strftime(
                EXPIRATION_FORMAT)
        self.assertEqual(formatted_expiration, "2025-12-31")

        # Test that not_valid_after (deprecated) produces warnings
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            _ = cert.not_valid_after
            # Check that a deprecation warning was issued
            self.assertTrue(len(w) > 0)
            self.assertTrue(any(
                "deprecated" in str(warning.message).lower() for warning in w))
