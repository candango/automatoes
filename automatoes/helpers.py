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


def confirm(msg, default=True):
    while True:
        choices = 'Y/n' if default else 'y/N'
        answer = input("{} [{}] ".format(msg, choices)).strip().lower()

        if answer in { 'yes', 'y' } or (default and not answer):
            return True
        elif answer in { 'no', 'n' } or (not default and not answer):
            return False
