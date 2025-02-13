# Copyright 2019-2025 Flavio Garcia
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
from automatoes.crypto import (generate_ari_data,
                               get_certificate_aki,
                               get_certificate_serial,
                               load_pem_certificate)
import base64
from cartola import fs
import unittest
import os


class ARITestCase(unittest.TestCase):
    """ Tests the crypto module from automatoes
    """

    def test_aki(self):
        """ Test the strip_certificate function """
        key_directory = os.path.join(FIXTURES_ROOT, "keys", "candango.org",
                                     "another")

        key_crt = fs.read(
            os.path.join(key_directory, "another.candango.org.crt"),
            True
        )

        pem_crt = load_pem_certificate(key_crt)

        aki = get_certificate_aki(pem_crt)
        serial = get_certificate_serial(pem_crt)
        expected_aki = ("c0:cc:03:46:b9:58:20:cc:5c:72:70:f3:e1:2e:cb:20:a6:"
                        "f5:68:3a")
        expected_serial = ("fa:f3:97:73:26:ea:e8:44:e7:14:00:20:ae:90:60:af:"
                           "ba:44")
        aki_b64 = base64.urlsafe_b64encode(expected_aki.encode())
        serial_b64 = base64.urlsafe_b64encode(expected_serial.encode())

        self.assertEqual(expected_aki, aki)
        self.assertEqual(expected_serial, serial)
        self.assertEqual(f"{aki_b64}.{serial_b64}", generate_ari_data(pem_crt))
