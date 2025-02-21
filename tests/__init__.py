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

from automatoes.protocol import AcmeV2Pesant, AcmeRequestsTransport
import os


TEST_ROOT = os.path.dirname(os.path.abspath(__file__))
FIXTURES_ROOT = os.path.abspath(os.path.join(TEST_ROOT, "fixtures"))
PROJECT_ROOT = os.path.abspath(os.path.join(TEST_ROOT, ".."))

PEEBLE_URL = "https://localhost:14000"


def get_transport() -> AcmeRequestsTransport:
    return AcmeRequestsTransport(PEEBLE_URL)


def get_protocol(transport: AcmeRequestsTransport = None) -> AcmeV2Pesant:
    if transport is None:
        transport = get_transport()
    return AcmeV2Pesant(
        transport,
        directory="dir",
        verify=get_absolute_path("certs/candango.minica.pem")
    )


def get_absolute_path(directory):
    return os.path.realpath(
            os.path.join(os.path.dirname(__file__), directory)
    )
