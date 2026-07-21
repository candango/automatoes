# Rust and PyO3

The repository is migrating the ACME V2 client and cryptography to a Rust
backend. PyO3 exposes that backend without breaking the existing Python API.
The current crate is the first production migration boundary, not a separate
feature track.

## Layout

```text
Cargo.toml                         Rust crate metadata
src/lib.rs                         PyO3 functions and module definition
pyproject.toml                     Maturin build configuration
automatoes/bin/rust_backend_example.py  Python usage example
rust_backend.pyi                   Editor-facing type signatures
```

The initial extension currently exposes:

```python
rust_backend.hello(name: str) -> str
rust_backend.add(left: int, right: int) -> int
rust_backend.sleep_detached(milliseconds: int) -> None
```

## Build in the project venv

```bash
source /home/fpiraz/venvs/candango_automatoes_env/bin/activate
maturin develop --release
python automatoes/bin/rust_backend_example.py
PYTHONPATH=. python tests/runrusttests.py
```

Expected output includes a Rust-generated greeting and `42`. The Rust test also
checks that a Python thread can run while `sleep_detached` is executing.

## Generate editor stubs

Native extension modules do not expose enough static information for a Python
language server. `pyo3-stubgen` generates a `.pyi` file from the installed
extension:

```bash
python -m pip install pyo3-stubgen
maturin develop --release
pyo3-stubgen rust_backend .
```

The generated `rust_backend.pyi` should remain next to the project root when
Neovim is opened at the repository root. Re-run it after changing exported
functions or signatures.

## Neovim language servers

The repository's Neovim setup uses Mason for `pylsp` and `rust_analyzer`. The
Mason Rust Analyzer is preferred over a broken or stale global binary. Restart
Neovim after Mason installs a server and open the repository root so Cargo
root detection finds `Cargo.toml`.

The stub file is for editor analysis only; it does not replace compiling and
installing the extension.

## Compatibility strategy

Existing Python users must continue using the same `AcmeV2`, cryptography,
model, serialization, and exception interfaces while the implementation moves
to Rust. Each migrated operation requires parity tests against the current
Python behavior before the Rust path becomes the default.

The intended rollout is:

1. Freeze the public Python contract with compatibility tests.
2. Port cryptographic primitives and JWS operations to Rust.
3. Port `AcmeV2` transport and order operations to Rust.
4. Keep the Python implementation as a temporary fallback during rollout.
5. Remove the fallback only after downstream compatibility is demonstrated.

CPU-heavy work and safe blocking operations should release the GIL. ACME
network latency remains part of the end-to-end runtime, so Rust primarily
improves local cryptography, serialization, parsing, and concurrency costs.
