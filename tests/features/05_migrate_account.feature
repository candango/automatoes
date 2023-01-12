# Copyright 2023 Flávio Gonçalves Garcia
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

Feature: Migrate account

  Scenario: Migrate an account register using certbot to automatoes
    # Enter steps here
    Given We have certbot account at /home/fpiraz/source/candango/tmp/certbot_work/accounts/acme-staging-v02.api.letsencrypt.org/directory/324e324a87602412c5dbd50fe530855e path
    #When We request nonce from ACME V2 server
    #Then ACME V2 server provides nonce in response headers
