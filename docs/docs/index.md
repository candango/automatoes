# Candango Automatoes

Automatoes is a Python ACME V2 client for manual certificate workflows and
advanced integrations. It preserves the `manuale` command while providing a
maintainable ACME implementation for account registration, authorization,
issuance, revocation, migration, and development-time integration testing.

## Project status

- Python package with Python 3.9+ support.
- ACME V2 client implementation.
- Pebble-backed integration suite for local validation.
- Rust/PyO3 is the target production backend for ACME V2 and cryptography.
- The existing Python API remains the compatibility surface during migration.
- Apache License 2.0.

## Choose a path

- [Getting started](getting-started.md) for installation and the first
  certificate workflow.
- [CLI reference](cli.md) for command behavior and options.
- [Architecture](architecture.md) for module and file boundaries.
- [Testing](testing.md) for unit tests, Pebble, and CI.
- [Rust and PyO3](rust-pyo3.md) for the native backend migration and extension workflow.
- [Security](security.md) for account keys, TLS trust, and test isolation.

## Support and contribution

Report defects and feature requests in the
[GitHub issue tracker](https://github.com/candango/automatoes/issues).

Before changing behavior, add or update a focused test. Keep persistent data,
commit messages, and code identifiers in English.
