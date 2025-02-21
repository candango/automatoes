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

from tests import FIXTURES_ROOT, get_protocol
from automatoes.crypto import (generate_ari_data,
                               get_certificate_aki,
                               get_certificate_serial,
                               load_pem_certificate)
import base64
from cartola import fs
import unittest
import os
from tornado import testing


class ARITestCase(testing.AsyncTestCase):
    """ Test letsencrypt nonce
    """

    @testing.gen_test
    async def test_nonce(self):
        protocol = get_protocol()
        # print(protocol.directory()['renewalInfo'])
        self.assertIsNotNone(protocol.new_nonce())


class AKISerialTestCase(unittest.TestCase):
    """ Test aki and serial fucntion to create the data to be sent for aki
    request
    """

    def setUp(self) -> None:
        key_directory = os.path.join(FIXTURES_ROOT, "keys", "candango.org",
                                     "another")
        key_crt = fs.read(
            os.path.join(key_directory, "another.candango.org.crt"),
            True
        )
        self.cert = load_pem_certificate(key_crt)

        self.expected_aki = ("c0:cc:03:46:b9:58:20:cc:5c:72:70:f3:e1:2e:cb:"
                             "20:a6:f5:68:3a")
        self.expected_serial = ("fa:f3:97:73:26:ea:e8:44:e7:14:00:20:ae:90:"
                                "60:af:ba:44")

    def test_aki_serial(self):
        """ Test cert aki and serial """
        aki = get_certificate_aki(self.cert)
        serial = get_certificate_serial(self.cert)
        self.assertEqual(self.expected_aki, aki)
        self.assertEqual(self.expected_serial, serial)

    def test_ari_data(self):
        """ Test ari_data from aki and serial """
        aki_b64 = base64.urlsafe_b64encode(self.expected_aki.encode())
        serial_b64 = base64.urlsafe_b64encode(self.expected_serial.encode())
        self.assertEqual(f"{aki_b64}.{serial_b64}",
                         generate_ari_data(self.cert))
