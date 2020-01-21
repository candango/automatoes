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
The moment you've been waiting for: actually getting SSL. For free!
"""

from . import get_version
from .acme import AcmeV2
from .authorize import update_order
from .crypto import (
    generate_rsa_key,
    load_private_key,
    export_private_key,
    create_csr,
    load_csr,
    export_csr_for_acme,
    load_pem_certificate,
    export_pem_certificate,
    strip_certificates,
)
from .errors import AutomatoesError
from .model import Order

import binascii
from cartola import fs, sysexits
from cryptography.hazmat.primitives.hashes import SHA256
import hashlib
import logging
import os
import sys

logger = logging.getLogger(__name__)

EXPIRATION_FORMAT = "%Y-%m-%d"


def issue(server, paths, account, domains, key_size, key_file=None,
          csr_file=None, output_path=None, must_staple=False, verbose=False):
    print("Candango Automatoes {}. Manuale replacement.\n\n".format(
        get_version()))

    current_path = paths['current']
    orders_path = paths['orders']
    domains_hash = hashlib.sha256(
        "_".join(domains).encode('ascii')).hexdigest()
    order_path = os.path.join(orders_path, domains_hash)
    order_file = os.path.join(order_path, "order.json".format(domains_hash))

    if not os.path.exists(orders_path):
        print(" ERROR: Orders path not found. Please run before: manuale "
              "authorize {}".format(" ".join(domains)))
        sys.exit(sysexits.EX_CANNOT_EXECUTE)
    else:
        if verbose:
            print("Orders path found at {}.".format(orders_path))

    if verbose:
        print("Searching order file {}.".format(order_file))

    if not os.path.exists(order_path):
        print(" ERROR: Order file not found. Please run before: manuale "
              "authorize {}".format(" ".join(domains)))
        sys.exit(sysexits.EX_CANNOT_EXECUTE)
    else:
        if verbose:
            print("Current order {} path found at orders path.\n".format(
                domains_hash))

    acme = AcmeV2(server, account)
    order = Order.deserialize(fs.read(order_file))
    if order.contents['status'] == "pending":
        if verbose:
            print("Querying ACME server for current status.")
        server_order = acme.query_order(order)
        order.contents = server_order.contents
        update_order(order, order_file)
        if order.contents['status'] in ["pending", "invalid"]:
            print(" ERROR: Order not ready or invalid. Please re-run: manuale"
                  " authorize {}.".format(" ".join(domains)))
            sys.exit(sysexits.EX_CANNOT_EXECUTE)
    elif order.contents['status'] == "invalid":
        print(" ERROR: Invalid order. Please re-run: manuale authorize "
              "{}.".format(" ".join(domains)))
        sys.exit(sysexits.EX_CANNOT_EXECUTE)

    if not output_path or output_path == '.':
        output_path = os.getcwd()

    # Load key if given
    if key_file:
        try:
            with open(key_file, 'rb') as f:
                certificate_key = load_private_key(f.read())
            order.key = export_private_key(certificate_key).decode('ascii')
            update_order(order, order_file)
        except (ValueError, AttributeError, TypeError, IOError) as e:
            print("ERROR: Couldn't read certificate key.")
            raise AutomatoesError(e)
    else:
        certificate_key = None

    # Load CSR or generate
    if csr_file:
        try:
            with open(csr_file, 'rb') as f:
                csr = export_csr_for_acme(load_csr(f.read()))
        except (ValueError, AttributeError, TypeError, IOError) as e:
            print("ERROR: Couldn't read CSR.")
            raise AutomatoesError(e)
    else:
        # Generate key
        if not key_file:
            if order.key is None:
                print("Generating a {} bit RSA key. This might take a "
                      "second.".format(key_size))
                certificate_key = generate_rsa_key(key_size)
                print("  Key generated.")
                order.key = export_private_key(certificate_key).decode('ascii')
                update_order(order, order_file)
                print("  Order updated with generated key.")
            else:
                print("Previous RSA key found in the order. Loading the key.")
                certificate_key = load_private_key(order.key.encode('ascii'))

        csr = create_csr(certificate_key, domains, must_staple=must_staple)

    try:
        logger.info("Requesting certificate issuance...")
        if order.contents['status'] == "ready":
            final_order = acme.finalize_order(order, csr)
            order.contents = final_order
            update_order(order, order_file)
            if final_order['status'] in ["processing", "valid"]:
                if verbose:
                    print("  Order {} finalized. Certificate is being "
                          "issued.".format(domains_hash))
            else:
                print(" ERROR: Order not ready or invalid. Please re-run: "
                      "manuale authorize {}.".format(" ".join(domains)))
                sys.exit(sysexits.EX_CANNOT_EXECUTE)
        elif order.contents['status'] in ["valid", "processing"]:
            print("  Order {} is already processing or valid. Downloading "
                  "certificate.".format(domains_hash))
        else:
            print(" ERROR: Order not ready or invalid. Please re-run: manuale "
                  "authorize {}.".format(" ".join(domains)))
            sys.exit(sysexits.EX_CANNOT_EXECUTE)

        if order.certificate_uri is None:
            if verbose:
                print("  Checking order {} status.".format(domains_hash))
            fulfillment = acme.await_for_order_fulfillment(order)
            if fulfillment['status'] == "valid":
                order.contents = fulfillment
                update_order(order, order_file)
            else:
                print(" ERROR: Order not ready or invalid. Please re-run: "
                      "manuale authorize {}.".format(" ".join(domains)))
                sys.exit(sysexits.EX_CANNOT_EXECUTE)
        else:
            print("  We already know the certificate uri for order {}. "
                  "Downloading certificate.".format(domains_hash))

        result = acme.download_order_certificate(order)

        logger.info("  Certificate downloaded.")
    except IOError as e:
        print("Connection or service request failed. Aborting.")
        raise AutomatoesError(e)

    try:
        certificates = strip_certificates(result.content)
        certificate = load_pem_certificate(certificates[0])

        # Print some neat info
        print("  Expires: {}".format(certificate.not_valid_after.strftime(
            EXPIRATION_FORMAT)))
        print("   SHA256: {}".format(binascii.hexlify(
            certificate.fingerprint(SHA256())).decode('ascii')))

        # Write the key, certificate and full chain
        os.makedirs(output_path, exist_ok=True)
        cert_path = os.path.join(output_path, domains[0] + '.crt')
        chain_path = os.path.join(output_path, domains[0] + '.chain.crt')
        intermediate_path = os.path.join(output_path,
                                         domains[0] + '.intermediate.crt')
        key_path = os.path.join(output_path, domains[0] + '.pem')

        if order.key is not None:
            with open(key_path, 'wb') as f:
                os.chmod(key_path, 0o600)
                f.write(order.key.encode('ascii'))
                print("\n  Wrote key to {}".format(f.name))

        with open(cert_path, 'wb') as f:
            f.write(export_pem_certificate(certificate))
            print("  Wrote certificate to {}".format(f.name))

        with open(chain_path, 'wb') as f:
            f.write(export_pem_certificate(certificate))
            if len(certificates) > 1:
                f.write(export_pem_certificate(load_pem_certificate(
                    certificates[1])))
            print("  Wrote certificate with intermediate to {}".format(f.name))

        if len(certificates) > 1:
            with open(intermediate_path, 'wb') as f:
                f.write(export_pem_certificate(load_pem_certificate(
                    certificates[1])))
                print("  Wrote intermediate certificate to {}".format(f.name))
    except IOError as e:
        print("  ERROR: Failed to write certificate or key. Going to print "
              "them for you instead.")
        if order.key is not None:
            for line in order.key.split('\n'):
                print("ERROR: {}".format(line))
        for line in export_pem_certificate(
                certificate).decode('ascii').split('\n'):
            print("ERROR: {}".format(line))
        raise AutomatoesError(e)
