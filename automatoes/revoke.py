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
The certificate revocation command.
"""

import logging

from . import get_version
from .acme import AcmeV2
from .errors import AutomatoesError
from .crypto import (
    load_pem_certificate,
    get_certificate_domains
)
from .helpers import confirm

logger = logging.getLogger(__name__)


def revoke(server, account, certificate):
    print("Candango Automatoes {}. Manuale replacement.\n\n".format(
        get_version()))

    # Load the certificate
    try:
        with open(certificate, 'rb') as f:
            certificate = load_pem_certificate(f.read())
    except IOError as e:
        print("ERROR: Couldn't read the certificate.")
        raise AutomatoesError(e)

    # Confirm
    print("Are you sure you want to revoke this certificate? It includes the "
          "following domains:")
    for domain in get_certificate_domains(certificate):
        print("  {}".format(domain))
    if not confirm("This can't be undone. Confirm?", default=False):
        raise AutomatoesError("Aborting.")

    # Revoke.
    acme = AcmeV2(server, account)
    try:
        acme.revoke_certificate(certificate)
    except IOError as e:
        raise AutomatoesError(e)

    print("Certificate revoked.")
