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

class AutomatoesError(Exception):
    pass


class AcmeError(IOError):
    def __init__(self, response):
        message = "The ACME request failed."
        try:
            details = response.json()
            self.type = details.get('type', 'unknown')
            message = "{} (type {}, HTTP {})".format(details.get('detail'),
                    self.type, response.status_code)
        except (ValueError, TypeError, AttributeError):
            pass
        super().__init__(message)


class AccountAlreadyExistsError(AcmeError):

    def __init__(self, response, existing_uri):
        super().__init__(response)
        self.existing_uri = existing_uri
