#!/usr/bin/env python
#
# Copyright 2019-2024 Flavio Garcia
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

import unittest
from tests import crypto_test


def suite():
    testLoader = unittest.TestLoader()
    alltests = unittest.TestSuite()
    alltests.addTests(testLoader.loadTestsFromModule(crypto_test))
    return alltests


if __name__ == "__main__":
    runner = unittest.TextTestRunner(verbosity=3)
    result = runner.run(suite())
    if not result.wasSuccessful():
        exit(2)
