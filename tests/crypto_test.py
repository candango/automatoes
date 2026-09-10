# Copyright 2019-2024 Flavio Garcia
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

from . import FIXTURES_ROOT
from automatoes.crypto import (
    generate_rsa_key,
    public_key_bytes,
    strip_certificates,
)
from cartola import fs
from cryptography.hazmat.primitives.serialization import (
    Encoding,
    PublicFormat,
)
import unittest
import os


class CryptoTestCase(unittest.TestCase):
    """ Tests the crypto module from automatoes
    """

    def test_strip_certificate(self):
        """ Test the strip_certificate function """
        key_directory = os.path.join(FIXTURES_ROOT, "keys", "candango.org",
                                     "another")
        chain_crt = fs.read(
            os.path.join(key_directory, "another.candango.org.chain.crt"),
            True
        )
        chain_crt_x = strip_certificates(chain_crt)
        self.assertEqual(2, len(chain_crt_x))

        key_crt = fs.read(
            os.path.join(key_directory, "another.candango.org.crt"),
            True
        )

        intermediate_crt = fs.read(
            os.path.join(key_directory,
                         "another.candango.org.intermediate.crt"),
            True
        )

        self.assertEqual(key_crt, chain_crt_x[0])
        self.assertEqual(intermediate_crt, chain_crt_x[1])

    def test_public_key_bytes_uses_subject_public_key_info(self):
        key = generate_rsa_key()
        expected = key.public_key().public_bytes(
            Encoding.DER,
            PublicFormat.SubjectPublicKeyInfo,
        )

        self.assertEqual(expected, public_key_bytes(key))
