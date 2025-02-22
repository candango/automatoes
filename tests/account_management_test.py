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

from automatoes.crypto import generate_rsa_key
from automatoes.model import Account
from cartola import security
from tests import get_protocol, get_transport, PEEBLE_URL
import unittest


class AccountTestCase(unittest.TestCase):
    """ Test letsencrypt nonce
    """

    def setUp(self) -> None:
        self.protocol = get_protocol(get_transport())

    def test_new_acount(self):
        contact = "candango_{}_{}@candango.org".format(
                security.random_string(5, False, False),
                security.random_string(5, False, False)
                )
        # To check against the get_registration method after
        # TODO: check against more than one emails in the contacts
        peeble_term = ("data:text/plain,Do%20what%20thou%20wilt")
        account = Account(key=generate_rsa_key(4096))
        response = self.protocol.new_account(account, [contact], True)
        self.assertEqual(peeble_term, response.terms)
        self.assertEqual("valid", response.status)
        urix = account.uri.split("/")
        self.assertEqual(PEEBLE_URL, "/".join(urix[0:3]))
        self.assertEqual("my-account", "/".join(urix[3:4]))
        self.assertIsInstance(urix[4:5][0], str)
        ordersx = account.orders.split("/")
        self.assertEqual(PEEBLE_URL, "/".join(ordersx[0:3]))
        self.assertEqual("list-orderz", "/".join(ordersx[3:4]))
        self.assertIsInstance(ordersx[4:5][0], str)
        self.assertEqual([f"mailto:{contact}"], account.contact)

    def test_get_acount(self):
        contact = "candango_{}_{}@candango.org".format(
                security.random_string(5, False, False),
                security.random_string(5, False, False)
                )
        account = Account(key=generate_rsa_key(4096))
        self.protocol.new_account(account, [contact], True)
        response = self.protocol.get_registration(account)
        self.assertEqual("valid", response.status)
        self.assertEqual(account.contact, response.contact)
        self.assertEqual(account.orders, response.orders)
