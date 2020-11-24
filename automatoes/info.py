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


"""
The account info command.
"""

from . import get_version
from .acme import AcmeV2
from .errors import AutomatoesError
import logging
import os

logger = logging.getLogger(__name__)


def info(server, account, paths):
    acme_v2 = AcmeV2(server, account)
    print("Candango Automatoes {}. Manuale replacement."
          "\n\n".format(get_version()))

    try:
        print("Requesting account data...\n")

        response = acme_v2.get_registration()
        print("  Account contacts:")
        for contact in response['contact']:
            print("    {}".format(contact[7:]))
        if "createdAt" in response:
            print("  Creation: {}".format(response['createdAt']))
        if "initialIp" in response:
            print("  Initial Ip: {}".format(response['initialIp']))
        if "key" in response:
            print("  Key Data:")
            print("    Type: {}".format(response['key']['kty']))
            print("    Public key (part I) n: {}".format(
                response['key']['n']))
            print("    Public key (part II) e: {}\n".format(
                response['key']['e']))
        else:
            print("    WARNING: Server won't return your key information.")
        print("    Private key stored at {}".format(
            os.path.join(paths['current'], "account.json")))
    except IOError as e:
        raise AutomatoesError(e)
