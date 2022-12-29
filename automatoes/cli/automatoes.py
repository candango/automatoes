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

from . import DEFAULT_ACCOUNT_PATH, LETS_ENCRYPT_PRODUCTION
from . import load_account
from .. import messages
from ..errors import AutomatoesError

from cartola import config, sysexits
import click
import os
import taskio
from taskio.core import TaskioCliContext

AUTOMATOES_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", ".."))
AUTOMATOES_CONFIG_PATH = os.path.join(AUTOMATOES_ROOT, "automatoes", "conf")
AUTOMATOES_CONFIG_FILE = os.path.join(AUTOMATOES_CONFIG_PATH, "automatoes.yml")


class AutomatoesCliContext(TaskioCliContext):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.AUTOMATOES_ROOT = AUTOMATOES_ROOT
        self.AUTOMATOES_CONFIG_PATH = AUTOMATOES_CONFIG_PATH
        self.AUTOMATOES_CONFIG_FILE = AUTOMATOES_CONFIG_FILE
        self.current_directory = os.getcwd()
        self.account = None
        self.server = None
        self.verbose = False
        self.root = None

    @property
    def account_files(self):
        return [account_file for account_file in
                os.listdir(self.current_directory)
                if "account.json" in account_file]


pass_context = click.make_pass_decorator(AutomatoesCliContext,
                                         ensure=True)


@taskio.root(taskio_conf=config.load_yaml_file(AUTOMATOES_CONFIG_FILE))
@click.option("-a", "--account", help=messages.OPTION_ACCOUNT_HELP,
              default=DEFAULT_ACCOUNT_PATH, show_default=True)
@click.option("-s", "--server", help=messages.OPTION_SERVER_HELP,
              default=LETS_ENCRYPT_PRODUCTION, show_default=True)
@pass_context
def automatoes_cli(ctx: AutomatoesCliContext, account, server):
    """ Interact with ACME certification authorities such as Let's Encrypt.

No idea what you're doing? Register an account, authorize your domains and
issue a certificate or two. Call a command with -h for more instructions.
    """
    try:
        account_model = load_account(account)
        ctx.account = account_model
    except AutomatoesError as ae:
        print(ae)
    ctx.server = server
