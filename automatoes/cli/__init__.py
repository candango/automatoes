# -*- coding: UTF-8 -*-
#
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

"""
The command line interface.
"""
from .. import get_version, messages
from ..authorize import authorize
from ..issue import issue
from ..info import info
from ..migrate import migrate
from ..model import Account
from ..register import register
from ..revoke import revoke
from ..upgrade import upgrade
from ..errors import AutomatoesError

import argparse
from cartola import sysexits
import logging
import os
import sys


logger = logging.getLogger(__name__)

# Defaults
LETS_ENCRYPT_PRODUCTION = "https://acme-v02.api.letsencrypt.org/"
DEFAULT_ACCOUNT_PATH = 'account.json'
DEFAULT_CERT_KEY_SIZE = 4096

AUTOMATOES_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", ".."))
AUTOMATOES_CONFIG_PATH = os.path.join(AUTOMATOES_ROOT, "automatoes", "conf")
AUTOMATOES_CONFIG_FILE = os.path.join(AUTOMATOES_CONFIG_PATH, "automatoes.yml")


# Command handlers
def _register(args):
    verbose = False
    if args.verbose > 0:
        verbose = True
    register(
        server=args.server,
        account_path=args.account,
        email=args.email,
        key_file=args.key_file,
        verbose=verbose
    )


def _authorize(args):
    paths = get_paths(args.account)
    account = load_account(args.account)
    verbose = False
    if args.verbose > 0:
        verbose = True
    authorize(args.server, paths, account, args.domain, args.method, verbose)


def _issue(args):
    paths = get_paths(args.account)
    account = load_account(args.account)
    verbose = False
    if args.verbose > 0:
        verbose = True
    issue(
        server=args.server,
        paths=paths,
        account=account,
        domains=args.domain,
        key_size=args.key_size,
        key_file=args.key_file,
        csr_file=args.csr_file,
        output_path=args.output,
        output_filename=args.output_filename,
        must_staple=args.ocsp_must_staple,
        verbose=verbose
    )


def _revoke(args):
    account = load_account(args.account)
    revoke(
        server=args.server,
        account=account,
        certificate=args.certificate
    )


def _info(args):
    paths = get_paths(args.account)
    account = load_account(args.account)
    info(args.server, account, paths)


def _upgrade(args):
    account_path = args.account
    account = load_account(args.account)
    upgrade(args.server, account, account_path)


def _migrate(args):
    migrate(account_path=args.account, certbot_path=args.certbot_path)


def get_paths(account_file):
    current_path = os.path.dirname(os.path.abspath(account_file))
    return {
        'authorizations': os.path.join(current_path, "authorizations"),
        'current': current_path,
        'orders': os.path.join(current_path, "orders"),
    }


def get_meta_paths(path):
    return {
        'orders': os.path.join(path, "orders"),
        'authorizations': os.path.join(path, "authorizations"),
    }


def load_account(path):
    # Show a more descriptive message if the file doesn't exist.
    if not os.path.exists(path):
        logger.error("Couldn't find an account file at {}.".format(path))
        logger.error("Are you in the right directory? Did you register yet?")
        logger.error("Run 'automatoes -h' for instructions.")
        raise AutomatoesError()

    try:
        # TODO: Use cartola fs.read here
        with open(path, 'rb') as f:
            return Account.deserialize(f.read())
    except (ValueError, IOError) as e:
        logger.error("Couldn't read account file. Aborting.")
        raise AutomatoesError(e)


class Formatter(argparse.ArgumentDefaultsHelpFormatter,
                argparse.RawDescriptionHelpFormatter):
    pass


def automatoes_main():
    print("The automatoes command is not implemented yet.")


# Where it all begins.
def manuale_main():
    parser = argparse.ArgumentParser(
        description=messages.DESCRIPTION,
        formatter_class=Formatter,
    )
    subparsers = parser.add_subparsers()

    # Server switch
    parser.add_argument('--server', '-s',
                        help=messages.OPTION_SERVER_HELP,
                        default=LETS_ENCRYPT_PRODUCTION)
    parser.add_argument('--account', '-a',
                        help=messages.OPTION_ACCOUNT_HELP,
                        default=DEFAULT_ACCOUNT_PATH)

    # Verbosity
    parser.add_argument('--verbose', '-v', action="count",
                        help="Set verbose mode", default=0)

    # Account creation
    register_sub = subparsers.add_parser(
        'register',
        help="Create a new account and register",
        description=messages.DESCRIPTION_REGISTER,
        formatter_class=Formatter,
    )
    register_sub.add_argument('email', type=str, help="Account e-mail address")
    register_sub.add_argument('--key-file', '-k',
                          help="Existing key file to use for the account")
    register_sub.set_defaults(func=_register)

    # Domain verification
    authorize_sub = subparsers.add_parser(
        'authorize',
        help="Verify domain ownership",
        description=messages.DESCRIPTION_AUTHORIZE,
        formatter_class=Formatter,
    )
    authorize_sub.add_argument('domain',
                           help="One or more domain names to authorize",
                           nargs='+')
    authorize_sub.add_argument('--method',
                           '-m',
                           help="Authorization method",
                           choices=('dns', 'http'),
                           default='dns')
    authorize_sub.set_defaults(func=_authorize)

    # Certificate issuance
    issue_sub = subparsers.add_parser(
        'issue',
        help="Request a new certificate",
        description=messages.DESCRIPTION_ISSUE,
        formatter_class=Formatter,
    )
    issue_sub.add_argument(
        'domain',
        help="One or more domain names to include in the certificate",
        nargs='+')
    issue_sub.add_argument('--key-size', '-b',
                       help="The key size to use for the certificate",
                       type=int, default=DEFAULT_CERT_KEY_SIZE)
    issue_sub.add_argument('--key-file', '-k',
                       help="Existing key file to use for the certificate")
    issue_sub.add_argument('--csr-file', help="Existing signing request to use")
    issue_sub.add_argument('--output', '-o',
                       help="The output directory for created objects",
                       default='.')
    issue_sub.add_argument('--output-filename',
                       help="The filename base for created objects",
                       default=None)
    issue_sub.add_argument('--ocsp-must-staple',
                       dest='ocsp_must_staple',
                       help="CSR: Request OCSP Must-Staple extension",
                       action='store_true')
    issue_sub.add_argument('--no-ocsp-must-staple',
                       dest='ocsp_must_staple',
                       help=argparse.SUPPRESS,
                       action='store_false')
    issue_sub.set_defaults(func=_issue, ocsp_must_staple=False)

    # Certificate revocation
    revoke_sub = subparsers.add_parser(
        'revoke',
        help="Revoke an issued certificate",
        description=messages.DESCRIPTION_REVOKE,
        formatter_class=Formatter,
    )
    revoke_sub.add_argument("certificate", help="The certificate file to "
                                                "revoke")
    revoke_sub.set_defaults(func=_revoke)

    # Account info
    info_sub = subparsers.add_parser(
        'info',
        help="Display account information",
        description=messages.DESCRIPTION_INFO,
        formatter_class=Formatter,
    )
    info_sub.set_defaults(func=_info)

    # Account upgrade
    upgrade_sub = subparsers.add_parser(
        'upgrade',
        help="Upgrade account's uri from Let's Encrypt ACME V1 to V2",
        description=messages.DESCRIPTION_UPGRADE,
        formatter_class=Formatter,
    )
    upgrade_sub.set_defaults(func=_upgrade)

    # Migrate an account from certbot
    migrate_sub = subparsers.add_parser(
        "migrate",
        help="Migrate a certbot account to automatoes format",
        description=messages.DESCRIPTION_MIGRATE,
        formatter_class=Formatter,
    )
    migrate_sub.add_argument("-c", "--certbot-path",
                         help="Directory path where the account files are"
                              "located")
    migrate_sub.set_defaults(func=_migrate)

    # Version
    version = subparsers.add_parser("version", help="Show the version number")
    version.set_defaults(func=lambda *args: logger.info(
        "automatoes {}\n\nThis tool is a full manuale "
        "replacement.\nJust run manuale instead of automatoes"
        ".".format(get_version())))

    # Parse
    args = parser.parse_args()
    if not hasattr(args, 'func'):
        parser.print_help()
        sys.exit(sysexits.EX_MISUSE)

    # Set up logging
    root = logging.getLogger('automatoes')
    root.setLevel(logging.INFO)
    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(logging.Formatter("%(message)s"))
    root.addHandler(handler)

    # Let's encrypt
    try:
        args.func(args)
    except AutomatoesError as e:
        if str(e):
            logger.error(e)
        sys.exit(sysexits.EX_SOFTWARE)
    except KeyboardInterrupt:
        logger.error("")
        logger.error("Interrupted.")
        sys.exit(sysexits.EX_TERMINATED_BY_CRTL_C)
    except Exception as e:
        logger.error("Oops! An unhandled error occurred. Please file a bug.")
        logger.exception(e)
        sys.exit(sysexits.EX_CATCHALL)
