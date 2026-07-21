# Architecture

## Runtime layers

```text
manuale / automatoes CLI
          |
          v
workflow modules (register, authorize, issue, revoke, migrate, upgrade)
          |
          v
AcmeV2 client and Peasant/Requests transport
          |
          v
ACME V2 server
```

## Important modules

| Module | Responsibility |
|---|---|
| `automatoes/acme.py` | ACME V2 account, order, challenge, certificate, and revocation operations |
| `automatoes/protocol.py` | Requests transport integration and custom CA verification |
| `automatoes/model.py` | Account, order, challenge, and registration data models |
| `automatoes/crypto.py` | RSA keys, CSRs, certificates, signatures, and Certbot key conversion |
| `automatoes/migrate.py` | Certbot account migration |
| `automatoes/issue.py` | Certificate output and chain handling |
| `automatoes/cli/` | Argument parsing and workflow dispatch |

## Persistent data

The manual workflow stores account and order state locally:

```text
account.json
orders/
  <domain-sequence-hash>/
    order.json
    *_challenge.json
certificates and keys
```

The account file contains the private account key and must be treated as a
secret. Order files contain server identifiers and workflow state; do not
rewrite or delete them while a workflow is active unless the command instructs
you to do so.

## ACME V2 order model

An order identifies a domain sequence. Authorization creates or resumes the
order, challenge validation moves it toward fulfillment, and issuance submits
a CSR whose identifiers must match the order. This is why changing domain
order between `authorize` and `issue` creates a different local order path.

## Rust production backend

Rust is the target implementation for the ACME V2 client and cryptography.
PyO3 provides the bridge while the established Python API remains stable for
existing consumers.

The migration boundary is:

```text
existing Python API
        |
        v
PyO3 compatibility facade
        |
        v
Rust AcmeV2 and cryptography implementation
```

Compatibility requirements are strict: preserve public function signatures,
models, serialization formats, exceptions, and observable behavior. Migration
is incremental, with the Python implementation available as a temporary
fallback while each contract is ported and verified.

The repository root currently contains the initial native boundary:

- `Cargo.toml` and `src/lib.rs` define the `rust_backend` extension.
- `pyproject.toml` makes Maturin the build backend.
- `automatoes/bin/rust_backend_example.py` demonstrates the Python API.
- `rust_backend.pyi` provides static signatures to editors.

The extension is therefore not an isolated experiment; it is the first step
of the production backend migration.
