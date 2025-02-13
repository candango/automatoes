# Candango Automat-o-es

[![PyPI](https://img.shields.io/pypi/v/automatoes.svg)](https://pypi.org/project/automatoes/)
[![Number of PyPI downloads](https://img.shields.io/pypi/dm/automatoes.svg)](https://pypi.org/project/automatoes/#files)
[![Build Status](https://img.shields.io/endpoint.svg?url=https%3A%2F%2Factions-badge.atrox.dev%2Fcandango%2Fautomatoes%2Fbadge&style=flat)](https://actions-badge.atrox.dev/candango/automatoes/goto)


Automatoes is a [Let's Encrypt](https://letsencrypt.org)/[ACME](https://github.com/ietf-wg-acme/acme/)
client for advanced users and developers. It is intended to be used by anyone
because we don't care if you're a robot, a processes or a person.

We will keep the `manuale` command to provide manual workflow designed by the
original project and to be a direct replacement from
[ManuaLE](https://github.com/veeti/manuale).

## Why?

Bacause Let's Encrypt's point is to be automatic and seamless and ManuaLE was
designed to be manual.

Automatoes will add automatic workflows and new features to evolve ManuaLe's
legacy. The project also will keep performing maintenance tasks as bug fixes
and refactory.

Automatoes is an ACME V2 replacement to ManuaLE.

## Features

* Simple interface with no hoops to jump through. Keys and certificate signing
requests are automatically generated: no more cryptic OpenSSL one-liners.
(However, you do need to know what to do with generated certificates and keys
yourself!)

* Support for DNS & HTTP validation. No need to figure out how to serve
challenge files from a live domain.

* Obviously, runs without root access. Use it from any machine you want, it
doesn't care. Internet connection recommended.

* Awful, undiscoverable name.

* And finally, if the `openssl` binary is your spirit animal after all, you can
still bring your own keys and/or CSR's. Everybody wins.

## Installation

Python 3.9 or above is required.

### Using your package manager

* TO DO

* Package maintainers wanted: your package here?


### Using pip

You can install the package from
[PyPI](https://pypi.python.org/pypi/automatoes) using the `pip` tool. To do 
so, run `pip3 install automatoes`.

If you're not using Windows or OS X pip may need to compile some of the
dependencies. In this case, you need a compiler and development headers for
Python, OpenSSL and libffi installed.

On Debian-based distributions, these will typically be
`gcc python3-dev libssl-dev libffi-dev`, and on RPM-based distributions
`gcc python3-devel openssl-devel libffi-devel`.

### From the git repository

    git clone https://github.com/candango/automatoes ~/.automatoes
    cd ~/.automatoes
    python3 -m venv env
    env/bin/python setup.py install
    ln -s env/bin/manuale ~/.bin/

(Assuming you have a `~/.bin/` directory in your `$PATH`).

## Quick start

Register an account (once):

    $ manuale register me@example.com

Authorize one or more domains:

    $ manuale authorize example.com
    DNS verification required. Make sure these records are in place:
      _acme-challenge.example.com. IN TXT "(some random gibberish)"
    Press Enter to continue.
    ...
    1 domain(s) authorized. Let's Encrypt!

Get your certificate:

    $ manuale issue --output certs/ example.com
    ...
    Certificate issued.

    Expires: 2016-06-01
     SHA256: (more random gibberish)

    Wrote key to certs/example.com.pem
    Wrote certificate to certs/example.com.crt
    Wrote certificate with intermediate to certs/example.com.chain.crt
    Wrote intermediate certificate to certs/example.com.intermediate.crt

Set yourself a reminder for renewal!

## Usage

You need to create an account once. To do so, call `manuale register [email]`.
This will create a new account key for you. Follow the registration
instructions.

Once that's done, you'll have your account saved in `account.json` in the
current directory. You'll need this to do anything useful. Oh, and it contains
your private key, so keep it safe and secure.

`manuale` expects the account file to be in your working directory by default,
so you'll probably want to make a specific directory to do all your certificate
stuff in. Likewise, created certificates get saved in the current path by
default.

Next up, verify the domains you want a certificate for with
`manuale authorize [domain]`. This will show you the DNS records you need to
create and wait for you to do it. For example, you might do it for
`example.com` and `www.example.com`.

Once that's done, you can finally get down to business.
Run `manuale issue example.com www.example.com` to get your certificate.
It'll save the key, certificate and certificate with intermediate to the
working directory.

There's plenty of documentation inside each command. Run `manuale -h` for a
list of commands and `manuale [command] -h` for details.

## Something different from ManuaLE?

Yes and no. Mostly yes, in the background.

Automatoes provides a manuale command replacement and a new automatoes command
that will be added in the future.

The manuale command will interface ACME V2 only as V1 is reaching
[End Of Life](https://community.letsencrypt.org/t/end-of-life-plan-for-acmev1/88430).

The account file structure from ManuaLE is maintained, no change here.

For Let's Encrypt servers it is necessary to change the uri from V1 api to V2.
With [#30](https://github.com/candango/automatoes/issues/30) we'll warn you
about your uri being Let's Encrypt ACME V1 and run with a correct ACME V2
without fixing the account.json file.

To fix the account.json file permanently run `manuale upgrade` and after
confirmation your account uri will be changed to the Let's Encrypt ACME V2 uri.

The upgrade action will only act against an account uri from production Let's
Encrypt ACME V1 otherwise nothing will be executed.

ACME V2 works with an 
[order workflow](https://tools.ietf.org/html/rfc8555#section-7.1) that must be
fulfilled. Automatoes will mimic orders in a file structure locally for better
control.

The manuale command will handle orders following the original project workflow
with minimal changes.

The automatoes command will be order based, let's talk about that when
released.

Here is what happens in the background(manuale replacement):

> `manuale authorize domain.com other.domain.com`
> 1. /acme/new-order is called and order file is stored locally at
> working_directory/orders/<sha256sum(domain.com other.domain.com)>/order.json
> 1. /acme/authz/challenge1 and /acme/authz/challenge2 are called and stored at
> working_directory/orders/<sha256sum(domain.com other.domain.com)>
> 1. the file name for challenges will be <domain>_challenge.json
> 1. you fulfill all challenges either by dns or http, dns is default.
> Just saying... you know the drill right? Same as before.
> 1. manuale the Let's Encrypt! message and you can issue the certificate

* If any challenge fails we delete the order file because it will be invalid
in the server side. Invalid orders are considered fulfilled and not pending,
we can discard them.
* If you hit Ctrl+c, the order will start from the state found in the local
file stored. Even challenges will be maintained, in a case when one challenge
is validated and 2 are pending, if Ctrl+c was hit, we'll recognize them in a 
next attempt.
* If you call the authorize command and there is an existent invalid order,
this one will be deleted, and a new order will be created.

> `manuale issue domain.com other.domain.com`

> 1. /acme/order/<order_id>/finalize is called with the pem generated
> or the one provided by you
> 1. /acme/cert/<cert_id> is called, and we place keys like we use to do before
> 1. we're done!

* If you try to issue certificates for a domain sequence and an oder is pending
or invalid, automatoes will ask you to run authorize before.

After authorizing a domain sequence you need run issue with the same domain
sequence because:

 1. The order file is stored at
 working_directory/orders/<sha256sum(domain.com other.domain.com)>
 if we change the domain sequence a new order file will be created at
 working_directory/orders/<sha256sum(other.domain.com domain.com)>
 2. The acme V2 order finalize call also requires something like this as
 described at
 [rfc8555 section-7.4](https://tools.ietf.org/html/rfc8555#section-7.4):

>  A request to finalize an order will result in an error if the CA is
   unwilling to issue a certificate corresponding to the submitted CSR.
   For example:
>
>   *  **If the CSR and order identifiers differ** <--- TALKING ABOUT THIS
>
>   *  If the account is not authorized for the identifiers indicated in the CSR
>
>   *  If the CSR requests extensions that the CA is not willing to include

Trying to keep thing as [KISS](https://www.acronymfinder.com/KISS.html) as
possible, we can complicate things later. Now we need ACME V2.

To create a certificate for a domain sequence authorized by a previous order
just:

 1. call authorize again. Chances are that no challenge will be needed, but it
 depends on the ACME V2 server implementation.
 1. fulfill challenge(s) if needed
 1. call issue with same domain sequence authorize
 1. we're done!

In other words, a domain sequence defines how the order identifier is created
locally.

The sha256sum command from coreutils can be used if you have a bash script
to monitor `manuale` execution:

```
> echo "domain.com other.domain.com" | sha256sum
83ccaf9441b1abea98837e2f4c2fc18122c0e9ee4e39dd1995387f4d5d495b69  -

> echo "other.domain.com domain.com" | sha256sum
d0bd2c4957537572ffb7150a7dc89e61f44f9ab603b75be481118e37ec5a6163  -
```

Storing meta files at working_directory/orders directory will let us
automate things better. Don't delete those files let Automatoes handle them for
you.

Here are more some features we can explore with this local file structure in
the future:

 - control and advise about limits, as Acme V2 enforce limits for opened orders
 per account
 - list orders and status (for pending orders)
 - create partial authorizations (that will be on automatoes command not in
 manuale)
 - SDK?
 - Can you imagine more? Create a feature request for us.

Also, the manuale command can be called with a verbose parameter(-v) right now
providing more output.

## See also

* [Best practices for server configuration](https://wiki.mozilla.org/Security/Server_Side_TLS)
* [Configuration generator for common servers](https://mozilla.github.io/server-side-tls/ssl-config-generator/)
* [Test your server](https://www.ssllabs.com/ssltest/)
* [Other clients](https://community.letsencrypt.org/t/list-of-client-implementations/2103)

## Support

For direct support create a
[new discussion](https://github.com/candango/automatoes/discussions/new?category=help)
or a
[new ticket](https://github.com/candango/automatoes/issues/new)
we'll love to see how to help you.

Automatoes is one of
[Candango Open Source Group](http://www.candango.org/projects/)
initiatives. Available under the
[Apache License, Version 2.0](http://www.apache.org/licenses/LICENSE-2.0.html).

This website and all documentation are licensed under
[Creative Commons 3.0](http://creativecommons.org/licenses/by/3.0/).

Copyright © 2019-2025 Flavio Garcia
Copyright © 2016-2017 Veeti Paananen under MIT License
