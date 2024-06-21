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

from . import get_absolute_path
from automatoes.protocol import AcmeV2Pesant, AcmeRequestsTransport
from tornado import testing


class NonceTestCase(testing.AsyncTestCase):
    """ Test letsencrypt nonce
    """

    @testing.gen_test
    async def test_auth(self):
        transport = AcmeRequestsTransport("https://localhost:14000")
        protocol = AcmeV2Pesant(
                transport,
                directory="dir",
                verify=get_absolute_path("certs/candango.minica.pem")
        )
        self.assertIsNotNone(protocol.new_nonce())
