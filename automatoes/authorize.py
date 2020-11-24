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

from . import get_version
from .acme import AcmeV2
from .crypto import generate_jwk_thumbprint
from .errors import AutomatoesError
from .model import Order

from cartola import fs, sysexits
import hashlib
import os
import sys


def create_order(acme, domains, method, order_file):
    order = acme.new_order(domains, method)
    update_order(order, order_file)
    return order


def update_order(order, order_file):
    fs.write(order_file, order.serialize().decode())


def clean_http_challenges(files):
    # Clean up created files
    for path in files:
        try:
            os.remove(path)
        except:
            print("Couldn't delete http challenge file {}".format(path))


def clean_challenge_file(challenge_file):
    try:
        os.remove(challenge_file)
    except:
        print("Couldn't delete challenge file {}".format(challenge_file))


def authorize(server, paths, account, domains, method, verbose=False):
    print("Candango Automatoes {}. Manuale replacement.\n\n".format(
        get_version()))

    current_path = paths['current']
    orders_path = paths['orders']
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
                print("  Found order file. Querying ACME server for current "
                      "status.")
            order = Order.deserialize(fs.read(order_file))
            try:
                server_order = acme.query_order(order)
                order.contents = server_order.contents
            except:
                print("    WARNING: Old order. Setting it as expired.\n")
                order.contents['status'] = "expired"
            update_order(order, order_file)

            if not order.expired and not order.invalid:
                if order.contents['status'] == 'valid':
                    print("  Order is valid and expires at {}. Please run "
                          "the issue "
                          "command.\n".format(order.contents['expires']))
                    print("  {} domain(s) authorized. Let's Encrypt!".format(
                        len(domains)))
                    sys.exit(sysexits.EX_OK)
                else:
                    if verbose:
                        print("    Order still pending and expires "
                              "at {}.\n".format(order.contents['expires']))
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
            print("  Requesting challenge for {}.".format(challenge.domain))
            if challenge.status == 'valid':
                print("    {} is already authorized until {}.".format(
                    challenge.domain, challenge.expires))
                continue
            else:
                challenge_file = os.path.join(order_path, challenge.file_name)
                if verbose:
                    print("    Creating challenge file {}.\n".format(
                        challenge.file_name))
                fs.write(challenge_file, challenge.serialize().decode())
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
                assert (token and os.path.sep not in token and '.' not in
                        token)
                files.add(token)
                fs.write(
                    os.path.join(current_path, token),
                    "%s.%s" % (token,
                               generate_jwk_thumbprint(account.key))
                )
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
                print("  {}: OK! Authorization lasts until {}.".format(
                    challenge.domain, challenge.expires))
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

        challenge_file = os.path.join(order_path, challenge.file_name)
        # Print results
        if failed:
            print("  {} domain(s) authorized, {} failed.".format(
                    len(done),
                    len(failed),
            ))
            print("  Authorized: {}".format(' '.join(done) or "N/A"))
            print("  Failed: {}".format(' '.join(failed)))
            print("  WARNING: The current order will be invalidated. "
                  "Try again.")
            if verbose:
                print("    Deleting invalid challenge file {}.\n".format(
                    challenge.file_name))
            clean_challenge_file(challenge_file)
            os.remove(order_file)
            os.rmdir(order_path)
            if method == 'http':
                print(files)
                clean_http_challenges(files)
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
                if verbose:
                    print("    Deleting valid challenge file {}.".format(
                        challenge.file_name))
                clean_challenge_file(challenge_file)
                if verbose:
                    print("    Querying ACME server for current status.\n")
                server_order = acme.query_order(order)
                order.contents = server_order.contents
                update_order(order, order_file)
                print("  {} domain(s) authorized. Let's Encrypt!".format(
                    len(done)))
        if method == 'http':
            clean_http_challenges(files)
        sys.exit(sysexits.EX_OK)
    except IOError as e:
        print("A connection or service error occurred. Aborting.")
        raise AutomatoesError(e)
