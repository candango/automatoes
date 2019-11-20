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

from behave import when, then
import os


def get_absolute_path(directory):
    return os.path.realpath(
        os.path.join(os.path.dirname(__file__), "..", "..", directory)
    )


@when("We have permission to create the user file at {directory}")
def step_we_have_permission_to_create_the_user_file(context, directory):
    real_directory = get_absolute_path(directory)
    context.tester.assertTrue(os.path.isdir(real_directory))
    context.tester.assertTrue(os.access(real_directory, os.W_OK))


@then("User file is created successfully at {account_path}")
def user_file_is_created_successfully(context, account_path):
    real_account_path = get_absolute_path(account_path)
    with open(real_account_path, 'wb') as f:
        os.chmod(real_account_path, 0o600)
        f.write(context.acme_v2.account.serialize())
    context.tester.assertTrue(os.path.exists(real_account_path))
    context.tester.assertTrue(os.path.isfile(real_account_path))
