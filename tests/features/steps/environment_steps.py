#!/usr/bin/env python
#
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

from automatoes.model import Account, Order
from behave import given, when, then, step
from cartola import fs
import os


def get_absolute_path(directory):
    return os.path.realpath(
        os.path.join(os.path.dirname(__file__), "..", "..", directory)
    )


def create_file(path, content, binary=False):
    real_path = get_absolute_path(path)
    fs.write(real_path, content, binary)
    os.chmod(real_path, 0o600)
    return real_path


@when("We have permission to create the user file at {directory}")
def step_we_have_permission_to_create_the_user_file(context, directory):
    real_directory = get_absolute_path(directory)
    context.tester.assertTrue(os.path.isdir(real_directory))
    context.tester.assertTrue(os.access(real_directory, os.W_OK))


@then("User file is created successfully at {account_path}")
def user_file_is_created_successfully(context, account_path):
    real_account_path = create_file(account_path,
                                    context.acme_v2.account.serialize(),
                                    True)
    context.tester.assertTrue(os.path.exists(real_account_path))
    context.tester.assertTrue(os.path.isfile(real_account_path))


@then("User contacts are stored at {account_path}")
def user_contacts_are_stored_at(context, account_path):
    # This is for further checking against get registration
    real_account_path = create_file(account_path,
                                    ",".join(context.user_contacts))
    context.tester.assertTrue(os.path.exists(real_account_path))
    context.tester.assertTrue(os.path.isfile(real_account_path))


@step("User contacts are read from {account_path}")
def user_contacts_are_read_from(context, account_path):
    user_contacts = None
    real_account_path = get_absolute_path(account_path)
    with open(real_account_path, 'r') as f:
        user_contacts = f.read()
    context.stored_user_contacts = user_contacts


@given("User file exists at {account_path}")
def user_file_exists_at(context, account_path):
    real_account_path = get_absolute_path(account_path)
    context.tester.assertTrue(os.path.exists(real_account_path))
    context.tester.assertTrue(os.path.isfile(real_account_path))
    data = None
    with open(real_account_path, 'r') as f:
        data = f.read()
    context.acme_v2.account = Account.deserialize(data)


@given("Certificate file exists at {certificate_path}")
def user_file_exists_at(context, certificate_path):
    real_certificate_path = get_absolute_path(certificate_path)
    context.tester.assertTrue(os.path.exists(real_certificate_path))
    context.tester.assertTrue(os.path.isfile(real_certificate_path))
    context.certificate = fs.read(real_certificate_path)


@then("Order file is stored at {order_path}")
def order_file_is_stored_at_path(context, order_path):
    real_order_path = create_file(order_path,
                                  context.order.serialize(),
                                  True)
    context.tester.assertTrue(os.path.exists(real_order_path))
    context.tester.assertTrue(os.path.isfile(real_order_path))


@then("Certificate file is stored at {certificate_path}")
def certificate_file_is_stored_at_path(context, certificate_path):
    real_certificate_path = create_file(certificate_path,
                                        context.certificate,
                                        True)
    context.tester.assertTrue(os.path.exists(real_certificate_path))
    context.tester.assertTrue(os.path.isfile(real_certificate_path))


@then("File is cleaned from {path}")
def order_file_is_stored_at_path(context, path):
    real_path = get_absolute_path(path)
    context.tester.assertTrue(os.path.exists(real_path))
    context.tester.assertTrue(os.path.isfile(real_path))
    os.remove(real_path)
    context.tester.assertFalse(os.path.exists(real_path))


@given("Order file exists at {order_path}")
def order_file_exists_at_path(context, order_path):
    real_order_path = get_absolute_path(order_path)
    context.tester.assertTrue(os.path.exists(real_order_path))
    context.tester.assertTrue(os.path.isfile(real_order_path))
    data = None
    with open(real_order_path, 'r') as f:
        data = f.read()
    context.order = Order.deserialize(data)
