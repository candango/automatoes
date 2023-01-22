# -*- coding: UTF-8 -*-
#
# Copyright 2019-2023 Flávio Gonçalves Garcia
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

from ..automatoes import pass_context, AutomatoesCliContext
from automatoes.model import Account
from cartola import fs
import taskio


@taskio.group(name="account", short_help="Group with commands related to "
                                         "account managment")
@pass_context
def account(ctx):
    pass


@account.command(name="list", short_help="List accounts")
@pass_context
def account_list(ctx: AutomatoesCliContext):
    from urllib.parse import urlparse
    print("Id\t\t\tServer")
    for account_file in ctx.account_files:
        default_account = True if account_file == "account.json" else False
        # if default_account:
        #     print("(Default Account)", end=" ")
        _account = Account.deserialize(fs.read(account_file))
        parsedurl = urlparse(_account.uri)
        account_id = parsedurl.path.split("/")[-1]
        account_server = "%s://%s" % (parsedurl.scheme, parsedurl.netloc)
        print("%s\t\t%s" % (account_id, account_server))
