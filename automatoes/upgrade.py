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
The account upgrade command.
"""

from . import get_version
from .acme import AcmeV2
from .errors import AutomatoesError
from .helpers import confirm
from cartola import fs
import logging

logger = logging.getLogger(__name__)


def upgrade(server, account, account_path):
    acme_v2 = AcmeV2(server, account, upgrade=True)
    print("Candango Automatoes {}. Manuale replacement."
          "\n\n".format(get_version()))
    if acme_v2.is_uri_letsencrypt_acme_v1():
        print("Account's uri format is Let's Encrypt ACME V1.")
        print("Current uri: %s" % acme_v2.account.uri)
        if not confirm("Let's Encrypt ACME V2: %s.\nDo you want to "
                       "upgrade?" % acme_v2.letsencrypt_acme_uri_v1_to_v2()):
            raise AutomatoesError("Aborting.")
        account.uri = acme_v2.letsencrypt_acme_uri_v1_to_v2()
        fs.write(account_path, account.serialize(), binary=True)
        print("Account's uri upgraded to Let's Encrypt ACME V2.\n")
    else:
        print("Account's uri format isn't Let's Encrypt ACME V1.")
        print("Skipping upgrade action.")
