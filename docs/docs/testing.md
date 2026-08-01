# Testing

Automatoes uses explicit `unittest` suites. ACME integration tests run against
Pebble and are separate from fast local unit tests.

## Unit tests

```bash
uv run python tests/runtests.py
```

These tests cover local crypto and certificate behavior without requiring a
running ACME server.

## Pebble integration tests

The integration suite requires Pebble on `https://localhost:14000` and the
local CA certificate under `tests/certs/`.

Start Pebble using the repository helper:

```bash
export GOPATH="$HOME/go"
./scripts/pebble_service.sh start tests/conf/pebble-config.json
```

Run the suite:

```bash
uv run python tests/runintegrationtests.py
```

The suite covers:

- ACME directory and replay nonce handling.
- Account registration and registration lookup.
- DNS, HTTP, wildcard, and multi-domain orders.
- Certificate download and revocation.
- Account, order, certificate, and contacts file round-trips.
- Certbot private-key and registration migration.

Pebble is configured for deterministic local tests. Its test environment may
set `PEBBLE_VA_ALWAYS_VALID`, `PEBBLE_VA_NOSLEEP`, and
`PEBBLE_WFE_NONCEREJECT`; these affect challenge behavior, not TLS certificate
verification.

## CI

GitHub Actions runs the unit suite, starts Pebble, runs the integration suite,
and then builds the package. The workflow is defined in
`.github/workflows/run_tests.yml`.

## Python and Rust development checks

For Python changes, run the project policy checker:

```bash
py-check path/to/changed_file.py
```

For the native extension:
```bash
cargo check
uv run maturin develop --release
uv run python tests/runrusttests.py
uv run python automatoes/bin/rust_backend_example.py
```

The Rust backend suite includes a GIL-release canary: a Rust sleep runs while
another Python thread must continue executing.

## Rust/Python parity tests

The Rust migration must preserve the public Python contract. Compatibility
tests should compare the Rust-backed path with the current Python behavior for
crypto results, JWS payloads, model serialization, exception types, and ACME
response handling. These tests are the release gate for switching the Rust
backend on by default.
