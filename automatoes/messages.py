# -*- coding: UTF-8 -*-
#
# Copyright 2019-2022 Flávio Gonçalves Garcia
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

from . import get_version

# Text
DESCRIPTION = """
Candango Automatoes {}. Manuale replacement.

Interact with ACME certification authorities such as Let's Encrypt.

No idea what you're doing? Register an account, authorize your domains and
issue a certificate or two. Call a command with -h for more instructions.
""".format(get_version())

DESCRIPTION_REGISTER = """
Creates a new account key and registers on the server. The resulting --account
is saved in the specified file, and required for most other operations.

You only have to do this once. Keep the account file safe and secure: it
contains your private key, and you need it to get certificates!
"""

DESCRIPTION_AUTHORIZE = """
Authorizes a domain or multiple domains for your account through DNS or HTTP
verification. You will need to set up DNS records or HTTP files as prompted.

After authorizing a domain, you can issue certificates for it. Authorizations
can last for a long time, so you might not need to do this every time you want
a new certificate.  This depends on the server being used. You should see an
expiration date for the authorization after completion.

If a domain is already authorized, the authorization's expiration date will be
printed.
"""

DESCRIPTION_ISSUE = """
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

DESCRIPTION_REVOKE = """
Revokes a certificate. The certificate must have been issued using the
current account.
"""

DESCRIPTION_INFO = """
Display registration info for the current account.
"""

DESCRIPTION_UPGRADE = """
Upgrade current account's uri from Let's Encrypt ACME V1 to ACME V2.
"""

OPTION_ACCOUNT_HELP = "The account file to use or create"
OPTION_SERVER_HELP = "The ACME server to use"
