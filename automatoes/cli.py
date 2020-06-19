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
The command line interface.
"""
from . import get_version
from .authorize import authorize
from .issue import issue
from .info import info
from .model import Account
from .register import register
from .revoke import revoke
from .upgrade import upgrade
from .errors import AutomatoesError

import argparse
from cartola import sysexits
import logging
import sys
import os

logger = logging.getLogger(__name__)

# Text
DESCRIPTION = \
"""
Candango Automatoes {}. Manuale replacement.

Interact with ACME certification authorities such as Let's Encrypt.

No idea what you're doing? Register an account, authorize your domains and
issue a certificate or two. Call a command with -h for more instructions.
""".format(get_version())

DESCRIPTION_REGISTER = \
"""
Creates a new account key and registers on the server. The resulting --account
is saved in the specified file, and required for most other operations.

You only have to do this once. Keep the account file safe and secure: it
contains your private key, and you need it to get certificates!
"""

DESCRIPTION_AUTHORIZE = \
"""
Authorizes a domain or multiple domains for your account through DNS or HTTP
verification. You will need to set up DNS records or HTTP files as prompted.

After authorizing a domain, you can issue certificates for it. Authorizations
can last for a long time, so you might not need to do this every time you want
a new certificate.  This depends on the server being used. You should see an
expiration date for the authorization after completion.

If a domain is already authorized, the authorization's expiration date will be
printed.
"""

DESCRIPTION_ISSUE = \
"""
Issues a certificate for one or more domains. Hopefully needless to say, you
must have valid authorizations for the domains you specify first.

This will generate a new RSA key and CSR for you. But if you want, you can
bring your own with the --key-file and --csr-file attributes. You can also set
a custom --key-size. (Don't try something stupid like 512, the server won't
accept it. I tried.)

The resulting key and certificate are written into domain.pem and domain.crt.
A chained certificate with the intermediate included is also written to
domain.chain.crt. You can change the --output directory to something else from
the working directory as well.

(If you're passing your own CSR, the given domains can be whatever you want.)

Note that unlike many other certification authorities, ACME does not add a
non-www or www alias to certificates. If you want this to happen, add it
yourself. You need to authorize both as well.

Certificate issuance has a server-side rate limit. Don't overdo it.
"""

DESCRIPTION_REVOKE = \
"""
Revokes a certificate. The certificate must have been issued using the
current account.
"""

DESCRIPTION_INFO = \
"""
Display registration info for the current account.
"""

DESCRIPTION_UPGRADE = \
"""
Upgrade current account's uri from Let's Encrypt ACME V1 to ACME V2.
"""

# Defaults
LETS_ENCRYPT_PRODUCTION = "https://acme-v02.api.letsencrypt.org/"
DEFAULT_ACCOUNT_PATH = 'account.json'
DEFAULT_CERT_KEY_SIZE = 4096


# Command handlers
def _register(args):
    register(
        server=args.server,
        account_path=args.account,
        email=args.email,
        key_file=args.key_file
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
        description=DESCRIPTION,
        formatter_class=Formatter,
    )
    subparsers = parser.add_subparsers()

    # Server switch
    parser.add_argument('--server', '-s', help="The ACME server to use",
                        default=LETS_ENCRYPT_PRODUCTION)
    parser.add_argument('--account', '-a',
                        help="The account file to use or create",
                        default=DEFAULT_ACCOUNT_PATH)

    # Verbosity
    parser.add_argument('--verbose', '-v', action="count",
                        help="Set verbose mode", default=0)

    # Account creation
    register = subparsers.add_parser(
        'register',
        help="Create a new account and register",
        description=DESCRIPTION_REGISTER,
        formatter_class=Formatter,
    )
    register.add_argument('email', type=str, help="Account e-mail address")
    register.add_argument('--key-file', '-k',
                          help="Existing key file to use for the account")
    register.set_defaults(func=_register)

    # Domain verification
    authorize = subparsers.add_parser(
        'authorize',
        help="Verify domain ownership",
        description=DESCRIPTION_AUTHORIZE,
        formatter_class=Formatter,
    )
    authorize.add_argument('domain',
                           help="One or more domain names to authorize",
                           nargs='+')
    authorize.add_argument('--method',
                           '-m',
                           help="Authorization method",
                           choices=('dns', 'http'),
                           default='dns')
    authorize.set_defaults(func=_authorize)

    # Certificate issuance
    issue = subparsers.add_parser(
        'issue',
        help="Request a new certificate",
        description=DESCRIPTION_ISSUE,
        formatter_class=Formatter,
    )
    issue.add_argument(
        'domain',
        help="One or more domain names to include in the certificate",
        nargs='+')
    issue.add_argument('--key-size', '-b',
                       help="The key size to use for the certificate",
                       type=int, default=DEFAULT_CERT_KEY_SIZE)
    issue.add_argument('--key-file', '-k',
                       help="Existing key file to use for the certificate")
    issue.add_argument('--csr-file', help="Existing signing request to use")
    issue.add_argument('--output', '-o',
                       help="The output directory for created objects",
                       default='.')
    issue.add_argument('--ocsp-must-staple',
                       dest='ocsp_must_staple',
                       help="CSR: Request OCSP Must-Staple extension",
                       action='store_true')
    issue.add_argument('--no-ocsp-must-staple',
                       dest='ocsp_must_staple',
                       help=argparse.SUPPRESS,
                       action='store_false')
    issue.set_defaults(func=_issue, ocsp_must_staple=False)

    # Certificate revocation
    revoke = subparsers.add_parser(
        'revoke',
        help="Revoke an issued certificate",
        description=DESCRIPTION_REVOKE,
        formatter_class=Formatter,
    )
    revoke.add_argument("certificate", help="The certificate file to revoke")
    revoke.set_defaults(func=_revoke)

    # Account info
    info = subparsers.add_parser(
        'info',
        help="Display account information",
        description=DESCRIPTION_INFO,
        formatter_class=Formatter,
    )
    info.set_defaults(func=_info)

    # Account upgrade
    upgrade = subparsers.add_parser(
        'upgrade',
        help="Upgrade account's uri from Let's Encrypt ACME V1 to V2",
        description=DESCRIPTION_UPGRADE,
        formatter_class=Formatter,
    )
    upgrade.set_defaults(func=_upgrade)

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
