# Copyright 2019-2023 Flávio Gonçalves Garcia
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

from .crypto import certbot_key_data_to_int, generate_rsa_key_from_parameters
from .errors import AutomatoesError
from .helpers import confirm
from .model import Account
from cartola import fs, sysexits
import json
import os
import sys


def migrate(account_path, certbot_path=None):
    if not certbot_path:
        certbot_path = input("Inform where is located the certbot account "
                             "path:")
    if not os.path.exists(certbot_path):
        print("ERROR: The informed path \"{}\" does not exist".format(
            certbot_path))
        sys.exit(sysexits.EX_CANNOT_EXECUTE)

    key_path = os.path.join(certbot_path, "private_key.json")
    regr_path = os.path.join(certbot_path, "regr.json")

    if not os.path.isfile(key_path):
        print("ERROR: The file private_key.json is not present at "
              "\"{}\"".format(certbot_path))
        sys.exit(sysexits.EX_CANNOT_EXECUTE)

    if not os.path.isfile(regr_path):
        print("ERROR: The file regr.json is not present at "
              "\"{}\"".format(certbot_path))
        sys.exit(sysexits.EX_CANNOT_EXECUTE)

    key_data = json.loads(fs.read(key_path))
    regr_data = json.loads(fs.read(regr_path))

    print("Migrating...")

    key_data_int = certbot_key_data_to_int(key_data)
    private_key = generate_rsa_key_from_parameters(
        key_data_int['p'], key_data_int['q'], key_data_int['d'],
        key_data_int['dp'], key_data_int['dq'], key_data_int['qi'],
        key_data_int['e'], key_data_int['n']
    )

    account = Account(key=private_key, uri=regr_data['uri'])

    if os.path.isfile(account_path):
        if not confirm("The account file account.json already exists."
                       "Continuing will overwrite it with the new migrated "
                       "key. Continue?", False):
            print("Aborting.")
            raise AutomatoesError("Aborting.")

    fs.write(account_path, account.serialize(), True)
    print("Wrote migrated account to {}.\n".format(account_path))
    print("What's next? Verify your domains with 'authorize' and use 'issue' "
          "to get new certificates.")
