# Automat-o-es

Automatoes is a [Let's Encrypt](https://letsencrypt.org)/[ACME](https://github.com/ietf-wg-acme/acme/) client for advanced users and developers. It is intended to be used by anyone because we don't care if you're a robot, a processes or a person.

Automatoes can be used as a direct replacement to [ManuaLE](https://github.com/veeti/manuale).

## Why?

Bacause Let's Encrypt's point is to be to be automatic and seamless and ManuaLE was great but it was refusing to add new features, fix bugs, refactor things, and [as pointed here](https://github.com/veeti/manuale/issues/41), suggested users to find a client being supported.

Well, let's keep the tool being supported and add api for developers create automated processes and features.

ManuaLE format and way to do things is awesome, that's why we need the this tool.

## TODO: Rebuild README from here!!!

## Features

* Simple interface with no hoops to jump through. Keys and certificate signing requests are automatically generated: no more cryptic OpenSSL one-liners. (However, you do need to know what to do with generated certificates and keys yourself!)

* Support for DNS & HTTP validation. No need to figure out how to serve challenge files from a live domain.

* Obviously, runs without root access. Use it from any machine you want, it doesn't care. Internet connection recommended.

* Awful, undiscoverable name.

* And finally, if the `openssl` binary is your spirit animal after all, you can still bring your own keys and/or CSR's. Everybody wins.

## Installation

Python 3.3 or above is required.

### Using your package manager

* Arch Linux: in the [AUR](https://aur.archlinux.org/packages/manuale).

* Fedora Linux: `dnf install manuale`.

* [Gentoo Linux](https://packages.gentoo.org/packages/app-crypt/manuale).

* Package maintainers wanted: your package here?

### Using Docker

There is a Docker image on the [Docker Hub](https://hub.docker.com/r/jgiannuzzi/letsencrypt-manuale/).

### Using pip

You can install the package from [PyPI](https://pypi.python.org/pypi/manuale) using the `pip` tool. To do so, run `pip3 install manuale`.

If you're not using Windows or OS X pip may need to compile some of the dependencies. In this case, you need a compiler and development headers for Python, OpenSSL and libffi installed.

On Debian-based distributions, these will typically be `gcc python3-dev libssl-dev libffi-dev`, and on RPM-based distributions `gcc python3-devel openssl-devel libffi-devel`.

### From the git repository

    git clone https://github.com/veeti/manuale ~/.manuale
    cd ~/.manuale
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

You need to create an account once. To do so, call `manuale register [email]`. This will create a new account key for you. Follow the registration instructions.

Once that's done, you'll have your account saved in `account.json` in the current directory. You'll need this to do anything useful. Oh, and it contains your private key, so keep it safe and secure.

`manuale` expects the account file to be in your working directory by default, so you'll probably want to make a specific directory to do all your certificate stuff in. Likewise, created certificates get saved in the current path by default.

Next up, verify the domains you want a certificate for with `manuale authorize [domain]`. This will show you the DNS records you need to create and wait for you to do it. For example, you might do it for `example.com` and `www.example.com`.

Once that's done, you can finally get down to business. Run `manuale issue example.com www.example.com` to get your certificate. It'll save the key, certificate and certificate with intermediate to the working directory.

There's plenty of documentation inside each command. Run `manuale -h` for a list of commands and `manuale [command] -h` for details.

## See also

* [Best practices for server configuration](https://wiki.mozilla.org/Security/Server_Side_TLS)
* [Configuration generator for common servers](https://mozilla.github.io/server-side-tls/ssl-config-generator/)
* [Test your server](https://www.ssllabs.com/ssltest/)
* [Other clients](https://community.letsencrypt.org/t/list-of-client-implementations/2103)

## License

**Apache License V2.0**

Copyright © 2019 Flavio Garcia

Copyright © 2016-2017 Veeti Paananen under MIT License
