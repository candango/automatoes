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

Feature: User Management

  Scenario: Create a new ACME V2 user

    Given We have a newAccount url from ACME V2 directory
    When We have permission to create the user file at features/sandbox
    And We ask to create an ACME V2 user
    Then User file is created successfully at features/sandbox/account.json
      And User contacts are stored at features/sandbox/user_contacts.txt

  Scenario: Retrieve existent ACME V2 user information

    Given User file exists at features/sandbox/account.json
    When We ask to get registration from ACME V2 user
      And User contacts are read from features/sandbox/user_contacts.txt
    Then Contacts from response match against stored ones
      And File is cleaned from features/sandbox/user_contacts.txt
      And File is cleaned from features/sandbox/account.json
