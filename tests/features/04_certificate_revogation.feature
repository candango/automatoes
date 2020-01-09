# Copyright 2019-2020 Flavio Garcia
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

Feature: ACME V2 Certificate revocation

  Scenario: Initialize user to authorize and issue domains
    Given We have a newAccount url from ACME V2 directory
    When We ask to create an ACME V2 user
    Then User file is created successfully at features/sandbox/account.json

  Scenario:  Create order and validate a domain

    Given User file exists at features/sandbox/account.json
    When We create new order for valid.candango.org by dns
      And We verify challenges from order for valid.candango.org by dns
      And We finalize order for valid.candango.org by dns
    Then Finalized order response status must be processing
      And We wait for fulfillment to be valid
      And Order file is stored at features/sandbox/valid.candango.org.order.json

  Scenario: Issue a certificate for a domain

    Given User file exists at features/sandbox/account.json
      And Order file exists at features/sandbox/valid.candango.org.order.json
    When Order has a certificate uri
      And We download valid.candango.org certificate
    Then Order has a certificate with valid.candango.org domain
      And File is cleaned from features/sandbox/valid.candango.org.order.json
      And Certificate file is stored at features/sandbox/valid.candango.org.cert

  Scenario: Revoke a certificate

    Given User file exists at features/sandbox/account.json
      And Certificate file exists at features/sandbox/valid.candango.org.cert
    When We revoke a certificate
    Then File is cleaned from features/sandbox/valid.candango.org.cert
      And File is cleaned from features/sandbox/account.json
