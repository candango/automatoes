# Candango Automatoes

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
