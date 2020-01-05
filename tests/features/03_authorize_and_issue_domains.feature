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

Feature: ACME V2 Authorize domains and issue certificates

  Scenario: Initialize user to authorize and issue domains
    Given We have a newAccount url from ACME V2 directory
    When We ask to create an ACME V2 user
    Then User file is created successfully at features/sandbox/account.json

  Scenario: Create order for one domain by dns

    Given User file exists at features/sandbox/account.json
    When We create new order for testdns.candango.org by dns
    Then Response identifiers and authorizations size must be 1
      And Order file is stored at features/sandbox/testdns.candango.org.order.json

  Scenario: Validate challenges and finalize order for one domain by dns

    Given User file exists at features/sandbox/account.json
      And Order file exists at features/sandbox/testdns.candango.org.order.json
    When We verify challenges from order for testdns.candango.org by dns
      And We finalize order for testdns.candango.org by dns
    Then Finalized order response status must be processing
      And We wait for fulfillment to be valid
      And Order file is stored at features/sandbox/testdns.candango.org.order.json

  Scenario: Issue a certificate for one domain by dns

    Given User file exists at features/sandbox/account.json
      And Order file exists at features/sandbox/testdns.candango.org.order.json
    When Order has a certificate uri
      And We download testdns.candango.org certificate
    Then Order has a certificate with testdns.candango.org domain
      And File is cleaned from features/sandbox/testdns.candango.org.order.json

   Scenario: Create order for wildcard domain by dns

    Given User file exists at features/sandbox/account.json
    When We create new order for *.candango.org by dns
    Then Response identifiers and authorizations size must be 1
      And Order file is stored at features/sandbox/wildcard.candango.org.order.json

  Scenario: Validate challenges and finalize order for wildcard domain by dns

    Given User file exists at features/sandbox/account.json
      And Order file exists at features/sandbox/wildcard.candango.org.order.json
    When We verify challenges from order for candango.org by dns
      And We finalize order for *.candango.org by dns
    Then Finalized order response status must be processing
      And We wait for fulfillment to be valid
      And Order file is stored at features/sandbox/wildcard.candango.org.order.json

  Scenario: Issue a certificate for wildcard domain by dns

    Given User file exists at features/sandbox/account.json
      And Order file exists at features/sandbox/wildcard.candango.org.order.json
    When Order has a certificate uri
      And We download *.candango.org certificate
    Then Order has a certificate with *.candango.org domain
      And File is cleaned from features/sandbox/wildcard.candango.org.order.json

  Scenario: Create order for multiple domains by dns

    Given User file exists at features/sandbox/account.json
    When We create new order for testmulti1.candango.org testmulti2.candango.org by dns
    Then Response identifiers and authorizations size must be 2
      And Order file is stored at features/sandbox/testmulti.candango.org.order.json

  Scenario: Validate challenges and finalize order for multiple domains by dns

    Given User file exists at features/sandbox/account.json
      And Order file exists at features/sandbox/testmulti.candango.org.order.json
    When We verify challenges from order for testmulti1.candango.org by dns
      And We verify challenges from order for testmulti2.candango.org by dns
      And We finalize order for testmulti1.candango.org testmulti2.candango.org by dns
    Then Finalized order response status must be processing
      And We wait for fulfillment to be valid
      And Order file is stored at features/sandbox/testmulti.candango.org.order.json

Scenario: Issue a certificate for multiple domains by dns

    Given User file exists at features/sandbox/account.json
      And Order file exists at features/sandbox/testmulti.candango.org.order.json
    When Order has a certificate uri
      And We download testmulti1.candango.org testmulti2.candango.org certificate
    Then Order has a certificate with testmulti1.candango.org domain
      And File is cleaned from features/sandbox/testmulti.candango.org.order.json


  Scenario: Creating order for one domain by http

    Given User file exists at features/sandbox/account.json
    When We create new order for testhttp.candango.org by http
    Then Response identifiers and authorizations size must be 1
      And Order file is stored at features/sandbox/testhttp.candango.org.order.json

  Scenario: Validate challenges and finalizing order for one domain by http

    Given User file exists at features/sandbox/account.json
      And Order file exists at features/sandbox/testhttp.candango.org.order.json
    When We verify challenges from order for testhttp.candango.org by http
      And We finalize order for testhttp.candango.org by http
    Then Finalized order response status must be processing
      And We wait for fulfillment to be valid
      And Order file is stored at features/sandbox/testhttp.candango.org.order.json


  Scenario: Issue a certificate for one domain by http

    Given User file exists at features/sandbox/account.json
      And Order file exists at features/sandbox/testhttp.candango.org.order.json
    When Order has a certificate uri
      And We download testhttp.candango.org certificate
    Then Order has a certificate with testhttp.candango.org domain
      And File is cleaned from features/sandbox/testhttp.candango.org.order.json
      And File is cleaned from features/sandbox/account.json