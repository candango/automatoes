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

# Staging server from:
# https://community.letsencrypt.org/t/staging-endpoint-for-acme-v2/49605
from behave import fixture, use_fixture
from automatoes.acme import AcmeV2
from automatoes.account import Account
import sys
import string
from unittest.case import TestCase

staging_url = "https://acme-staging-v02.api.letsencrypt.org"


def random_string(length=5, upper_chars=True, punctuation=False):
    """
    TODO: From firenado.security module. Maybe use it for tests?
    Generate a random string with the size equal to the given length.

    The string is based on random choices from a sequence of ascii lower case
    characters and digits.

    If length is not informed the string size will be 5.
    """
    chars = string.ascii_lowercase + string.digits
    if upper_chars:
        chars += string.ascii_uppercase
    if punctuation:
        chars += string.punctuation
    if sys.version_info < (3, 6):
        import random
        return ''.join(
            random.SystemRandom().choice(chars) for _ in range(length)
        )
    else:
        import secrets
        return ''.join(secrets.choice(chars) for _ in range(length))

@fixture
def acme_v2(context, timeout=1, **kwargs):
    context.acme_v2 = AcmeV2(staging_url, None)
    yield context.acme_v2


@fixture
def random_string_function(context, timeout=1, **kwargs):
    context.random_string = random_string
    yield context.random_string

@fixture
def staging_url_context(context, timeout=1, **kwargs):
    context.staging_url = staging_url
    yield context.staging_url

@fixture
def tester(context, timeout=1, **kwargs):
    context.tester = TestCase()
    yield context.tester


def before_all(context):
    use_fixture(acme_v2, context)
    use_fixture(random_string_function, context)
    use_fixture(staging_url_context, context)
    use_fixture(tester, context)
