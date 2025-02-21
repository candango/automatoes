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

from tests import get_protocol, get_transport
from tornado import testing


class NonceTestCase(testing.AsyncTestCase):
    """ Test letsencrypt nonce
    """

    @testing.gen_test
    async def test_nonce(self):
        protocol = get_protocol(get_transport())
        print(protocol.new_nonce())
        self.assertIsNotNone(protocol.new_nonce())
