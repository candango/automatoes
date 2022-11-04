# Candango Automatoes

# What's new in Automatoes 0.9.7

## Oct 14, 2022

We are pleased to announce the release of Automatoes 0.9.8.

This release won't support Python 3.5. Use a python newer than 3.6 for now on.

Here are the highlights:


## Build

 * Migrate from travis to github actions build #79 
 * Depreciate python 3.5 #86 

## Bugs

* Registration error due to unicode to utf-8 decode error #103 

## Features

 * Add account uri, id and status to the manuale info command  #106 
 * Make manuale register verbose feature #107 



# What's new in Automatoes 0.9.7

## Feb 20, 2020

We are pleased to announce the release of Automatoes 0.9.7.

This is a security fix that address CVE-2020-36242 updating cryptography to a
patched version.

We still support python 3.5 but the cryptography being installed won't be
patched against CVE-2020-36242.

It is recommended to upgrade your Python version as Python 3.5 is no longer
maintained (end of life was September 13th, 2020) and cryptography dropped
python 3.5 support.

Here are the highlights:

## Security

* CVE-2020-36242: Symmetrically encrypting large values can lead to integer overflow #84

## Bugs

* Suppress crypto.py warning on Python 3.5 #83


# What's new in Automatoes 0.9.6

## Nov 25, 2020

We are pleased to announce the release of Automatoes 0.9.6.

This release finally fixes the issue where an expired order will prevent the
user of refreshing a certificate and adds more support to other ACME V2 clients
that follow rfc8555 loosely. Tested against 
[Buypass GO](https://www.buypass.com/ssl/products/acme) ACME V2.  

Here are the highlights:

## Bugs

* To renew a certificate it is necessary to delete its order file #39
* Fix url handling when acme is served with paths #71

## Features

* Set expiration date to the order if server won't do it #72
* Show only information provided by the server with manuale info #73


# What's new in Automatoes 0.9.5

## Aug 07, 2020

We are pleased to announce the release of Automatoes 0.9.5.

Here are the highlights:

## Bugs

* Missing 'certificate' key in finalize response bug #42

See cached version: https://web.archive.org/web/20200930224131/https://github.com/candango/automatoes/releases/tag/v0.9.5


# What's new in Automatoes 0.9.4

## Jul 20, 2020

We are pleased to announce the release of Automatoes 0.9.4.

This release fixes the http authorization method and account registration
broken by 0.9.3.

Here are the highlights:

## Bugs

* Content generated into the http challenge file is invalid #44
* Cannot register account #53

See cached version: https://web.archive.org/web/20200930224131/https://github.com/candango/automatoes/releases/tag/v0.9.4


# What's new in Automatoes 0.9.3

## Jun 24, 2020

We are pleased to announce the release of Automatoes 0.9.3.

This release will detect if account is using Let's Encrypt ACME V1 uri and fix
execution to run with ACME V2.
A new command `manuale update` was added to fix Let's Encrypt ACME V1 uri to
ACME V2 permanently.
Also, we install on Pip 20.1.x and up.

A gitter chat was added for faster support. Just ping us there, and we'll try
to help you with your issue.

Here are the highlights:

## Features

* Upgrade existent account from acme v1 to acme v2 #30
* Add gitter chat for faster support. feature #48

## Bugs

* Handle better error codes from cli bug #41
* Pip 20.1 will break installation bug #43

See cached version: https://web.archive.org/web/20200930224131/https://github.com/candango/automatoes/releases/tag/v0.9.3


# What's new in Automatoes 0.9.1

## Jan 29, 2020

We are pleased to announce the release of Automatoes 0.9.1.

This release fixes a severe bug with `manuale revoke` command and updates dependencies.

Here are the highlights:

## Bugs

 * Revoke dies with AttributeError: 'str' object has no attribute 'public_bytes' bug severe. [#34](https://github.com/candango/automatoes/issues/34)


# What's new in Automatoes 0.9.0

## Jan 21, 2020

We are pleased to announce the release of Automatoes 0.9.0.

Candango Automatoes as a ACME V2 replacement for ManuaLE.

Here are the highlights:

## New Features

 * Created test environment. #3
 * Created mock server to test challenges. #10
 * Random string and uuid command line tasks. #284

## Refactory

 * ACME V2 account registration. [#5](https://github.com/candango/automatoes/issues/5)
 * ACME V2 get nonce. [#7](https://github.com/candango/automatoes/issues/7)
 * ACME V2 Account Info. [#16](https://github.com/candango/automatoes/issues/16)
 * ACME V2 Applying for Certificate Issuance. [#18](https://github.com/candango/automatoes/issues/18)
 * ACME V2 Certificate Revocation [#25](https://github.com/candango/automatoes/issues/25)

# What's new in Automatoes 0.0.0.1

## Oct 09, 2019

We are pleased to announce the release of Automatoes 0.0.0.1.

Candango Automatoes initial rlease.

## Bugs

 * Python 3.5 depreciation notice. [#6](https://github.com/candango/automatoes/issues/6)

## Refactory

 * Changed license to Apache 2. [#2](https://github.com/candango/automatoes/issues/2)

# Manuale (Legacy)

## 1.1.0 (January 1, 2017)

* Added support for HTTP authorization. (contributed by GitHub user @mbr)

* Added support for registration with an existing key. (contributed by GitHub
user @haddoncd)

* Using an existing CSR no longer requires the private key. (contributed by
GitHub user @eroen)

## 1.0.3 (August 27, 2016)

* Fixed handling of recycled authorizations: if a domain is already authorized,
 the server no longer allows reauthorizing it until expired.

* Existing EC keys can now be used to issue certificates. (Support for
generating EC keys is not yet implemented.)

## 1.0.2 (March 20, 2016)

* The authorization command now outputs proper DNS record lines.

## 1.0.1 (February 9, 2016)

* Private key files are now created with read permission for the owner only
(`0600` mode).

* The README is now converted into reStructuredText for display in PyPI.

* Classified as Python 3 only in PyPI.

## 1.0.0 (February 6, 2016)

Initial release.
