# Copyright 2019-2024 Flavio Garcia
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

# Staging server from:
# https://community.letsencrypt.org/t/staging-endpoint-for-acme-v2/49605
from behave import fixture, use_fixture
from automatoes.acme import AcmeV2
from automatoes.protocol import AcmeV2Pesant, AcmeRequestsTransport
import os
from unittest.case import TestCase

peeble_url = "https://localhost:14000"


def get_absolute_path(directory):
    return os.path.realpath(
        os.path.join(os.path.dirname(__file__), "..", directory)
    )


@fixture
def acme_protocol(context, timeout=1, **kwargs):
    transport = AcmeRequestsTransport(peeble_url)
    context.acme_protocol = AcmeV2Pesant(
        transport,
        url=peeble_url,
        directory="dir",
        verify=get_absolute_path("certs/candango.minica.pem")
    )
    yield context.acme_protocol


@fixture
def acme_v2(context, timeout=1, **kwargs):
    context.acme_v2 = AcmeV2(
        peeble_url,
        None,
        directory="dir",
        verify=get_absolute_path("certs/candango.minica.pem")
    )
    yield context.acme_v2


@fixture
def peeble_url_context(context, timeout=1, **kwargs):
    context.peeble_url = peeble_url
    yield context.peeble_url


@fixture
def tester(context, timeout=1, **kwargs):
    context.tester = TestCase()
    yield context.tester


def before_all(context):
    use_fixture(acme_protocol, context)
    use_fixture(acme_v2, context)
    use_fixture(peeble_url_context, context)
    use_fixture(tester, context)
