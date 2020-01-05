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
The domain authorization command.
"""

import logging
import time
import hashlib
import os
import sys
from cartola import fs, sysexits

from . import get_version
from .acme import AcmeV2
from .crypto import generate_jwk_thumbprint, jose_b64
from .errors import AutomatoesError
from .model import Order

logger = logging.getLogger(__name__)


def get_challenge(auth, auth_type):
    try:
        return [ch for ch in auth.get('challenges', [])
                if ch.get('type') == auth_type][0]
    except IndexError:
        raise AutomatoesError("The server didn't return a '{}' "
                           "challenge.".format(auth_type))


def retrieve_verification(acme, domain, auth, method):
    while True:
        logger.info("{}: waiting for verification. Checking in 5 "
                    "seconds.".format(domain))
        time.sleep(5)

        response = acme.get_authorization(auth['uri'])
        status = response.get('status')
        if status == 'valid':
            logger.info("{}: OK! Authorization lasts until {}.".format(
                domain, response.get('expires', '(not provided)')))
            return True
        elif status != 'pending':
            # Failed, dig up details
            error_type, error_reason = "unknown", "N/A"
            try:
                challenge = get_challenge(response, method)
                error_type = challenge.get('error').get('type')
                error_reason = challenge.get('error').get('detail')
            except (AutomatoesError, ValueError, IndexError, AttributeError,
                    TypeError):
                pass

            logger.info("{}: {} ({})".format(domain, error_reason, error_type))
            return False


def create_order(acme, domains, method, order_file):
    order = acme.new_order(domains, method)
    update_order(order, order_file)
    return order


def update_order(order, order_file):
    fs.write(order_file, order.serialize().decode())


def authorize(server, paths, account, domains, method, verbose=False):
    print("Candango Automatoes {}. Manuale replacement."
          "\n\n".format(get_version()))

    current_path = paths['current']
    orders_path = paths['orders']
    authorizations_path = paths['authorizations']
    domains_hash = hashlib.sha256(
        "_".join(domains).encode('ascii')).hexdigest()
    order_path = os.path.join(orders_path, domains_hash)
    order_file = os.path.join(order_path, "order.json".format(domains_hash))

    if not os.path.exists(orders_path):
        if verbose:
            print("Orders path not found creating it at {}."
                  "".format(orders_path))
        os.mkdir(orders_path)
        os.chmod(orders_path, 0o770)
    else:
        if verbose:
            print("Orders path found at {}.".format(orders_path))

    if not os.path.exists(order_path):
        if verbose:
            print("Current order {} path not found creating it at orders "
                  "path.\n".format(domains_hash))
        os.mkdir(order_path)
        os.chmod(order_path, 0o770)
    else:
        if verbose:
            print("Current order {} path found at orders path.\n".format(
                domains_hash))

    method = method
    acme = AcmeV2(server, account)

    try:
        print("Authorizing {}.\n".format(", ".join(domains)))
        # Creating orders for domains if not existent
        if not os.path.exists(order_file):
            if verbose:
                print("  Order file not found creating it.")
            order = create_order(acme, domains, method, order_file)
        else:
            if verbose:
                logger.info(
                    "  Found order file. Querying ACME server for current "
                    "status."
                )
            order = Order.deserialize(fs.read(order_file))
            server_order = acme.query_order(order)
            order.contents = server_order.contents
            update_order(order, order_file)

            if not order.expired and not order.invalid:
                if verbose:
                    print("    Order still valid and expires at {}.\n".format(
                        order.contents['expires']))
            else:
                if order.invalid:
                    print("    WARNING: Invalid order, renewing it.\n    Just "
                          "continue with the authorization when all "
                          "verifications are in place.\n")
                else:
                    print("  WARNING: Expired order. Renewing order.\n")
                os.remove(order_file)
                order = create_order(acme, domains, method, order_file)
                update_order(order, order_file)

        pending_challenges = []

        for challenge in acme.get_order_challenges(order):
            logger.info("  Requesting challenge for {}.".format(
                challenge.domain))
            if challenge.status == 'valid':
                print("    {} is already authorized until {}.".format(
                    challenge.domain, challenge.expires))
                continue
            else:
                pending_challenges.append(challenge)

        # Quit if nothing to authorize
        if not pending_challenges:
            print("\nAll domains are already authorized, exiting.")
            sys.exit(sysexits.EX_OK)

        files = set()
        if method == 'dns':
            print("\n  DNS verification required. Make sure these TXT records"
                  " are in place:\n")
            for challenge in pending_challenges:
                print("    _acme-challenge.{}.  IN TXT  "
                      "\"{}\"".format(challenge.domain, challenge.key))
        elif method == 'http':
            print("\n  HTTP verification required. Make sure these files are "
                  "in place:\n")
            for challenge in pending_challenges:
                token = challenge.contents['token']

                # path sanity check
                assert (token and os.path.sep not in token and '.' not in token)
                files.add(token)
                fs.write(os.path.join(current_path, token), challenge.key)
                print("    http://{}/.well-known/acme-challenge/{}".format(
                    challenge.domain, token))

            print("\n  The necessary files have been written to the current "
                  "directory.\n")
        # Wait for the user to complete the challenges
        input("\nPress Enter to continue.\n")

        # Validate challenges
        done, failed, pending = set(), set(), set()
        for challenge in pending_challenges:
            print("  {}: waiting for verification. Checking in 5 "
                  "seconds.".format(challenge.domain))
            response = acme.verify_order_challenge(challenge, 5, 1)
            if response['status'] == "valid":
                print(response)
                print("{}: OK! Authorization lasts until {}.".format(
                    challenge.domain, response['expires']))
                done.add(challenge.domain)
            elif response['status'] == 'invalid':
                print("  {}: {} ({})".format(
                    challenge.domain,
                    response['error']['detail'],
                    response['error']['type'])
                )
                failed.add(challenge.domain)
                break
            else:
                print("{}: Pending!".format(challenge.domain))
                pending.add(challenge.domain)
                break

        # Print results
        if failed:
            print("  {} domain(s) authorized, {} failed, {} pending.".format(
                    len(done),
                    len(failed),
                    len(pending),
            ))
            print("  Authorized: {}".format(' '.join(done) or "N/A"))
            print("  Failed: {}".format(' '.join(failed)))
            print("  Pending: {}".format(' '.join(pending) or "N/A"))
            print("  The current order will be invalidated. Try again.")
            os.remove(order_file)
            os.rmdir(order_path)
            sys.exit(sysexits.EX_FATAL_ERROR)
        else:
            if pending:
                print("  {} domain(s) authorized, {} pending.".format(
                    len(done),
                    len(pending)))
                print("  Authorized: {}".format(' '.join(done) or "N/A"))
                print("  Pending: {}".format(' '.join(pending)))
                print("  Try again.")
                sys.exit(sysexits.EX_CANNOT_EXECUTE)
            else:
                logger.info("  {} domain(s) authorized. Let's Encrypt!".format(
                    len(done)))
        sys.exit(sysexits.EX_OK)


        for domain in domains:

            logger.info("Requesting challenge for {}.".format(domain))
            created = acme.new_authorization(domain)
            auth = created.contents
            auth['uri'] = created.uri

            # Check if domain is already authorized
            if auth.get('status') == 'valid':
                logger.info("{} is already authorized until {}.".format(domain, auth.get('expires', '(unknown)')))
                continue

            # Find the challenge and calculate values
            auth['challenge'] = get_challenge(auth, method)
            auth['key_authorization'] = "{}.{}".format(auth['challenge'].get('token'), thumbprint)
            digest = hashlib.sha256()
            digest.update(auth['key_authorization'].encode('ascii'))
            auth['txt_record'] = jose_b64(digest.digest())

            authz[domain] = auth

        # Quit if nothing to authorize
        if not authz:
            logger.info("")
            logger.info("All domains are already authorized, exiting.")
            return

        # Print challenges
        files = set()
        logger.info("")
        if method == 'dns-01':
            logger.info("DNS verification required. Make sure these TXT records are in place:")
            logger.info("")
            for domain, auth in authz.items():
                logger.info("  _acme-challenge.{}.  IN TXT  \"{}\"".format(domain, auth['txt_record']))
        elif method == 'http-01':
            logger.info("HTTP verification required. Make sure these files are in place:")
            logger.info("")
            for domain, auth in authz.items():
                token = auth['challenge'].get('token')

                # path sanity check
                assert (token and os.path.sep not in token and '.' not in token)
                files.add(token)
                with open(token, 'w') as out:
                    out.write(auth['key_authorization'])

                logger.info("  http://{}/.well-known/acme-challenge/{}".format(domain, token))
            logger.info("")
            logger.info("The necessary files have been written to the current directory.")

        # Wait for the user to complete the challenges
        logger.info("")
        input("Press Enter to continue.")

        # Validate challenges
        done, failed = set(), set()
        for domain, auth in authz.items():
            logger.info("")
            challenge = auth['challenge']
            acme.validate_authorization(challenge['uri'], method, auth['key_authorization'])
            if retrieve_verification(acme, domain, auth, method):
                done.add(domain)
            else:
                failed.add(domain)

        # Print results
        logger.info("")
        if failed:
            logger.info("{} domain(s) authorized, {} failed.".format(len(done), len(failed)))
            logger.info("Authorized: {}".format(' '.join(done) or "N/A"))
            logger.info("Failed: {}".format(' '.join(failed)))
        else:
            logger.info("{} domain(s) authorized. Let's Encrypt!".format(len(done)))

        # Clean up created files
        for path in files:
            try:
                os.remove(path)
            except:
                logger.info("")
                logger.exception("Couldn't delete challenge file {}".format(path))
    except IOError as e:
        logger.error("A connection or service error occurred. Aborting.")
        raise AutomatoesError(e)
