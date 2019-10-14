#!/usr/bin/env python
#
# Copyright 2019 Flavio Garcia
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

from behave import given, when, then


@given("ACME V2 server is accessible")
def step_v2_server_is_accessible(context):
    response = context.acme_v2.get_directory()
    assert response.status_code == 200


@when("We request nounce from ACME V2 server")
def step_we_request_nounce_from_acme_v2_server(context):
    context.nounce = context.acme_v2.get_nonce()


@then("ACME V2 server provides nounce in response headers")
def step_acme_v2_server_provides_nounce_in_response_headers(context):
    assert not context.nounce is None
