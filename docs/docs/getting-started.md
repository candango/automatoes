# Getting started

## Requirements

- Python 3.9 or newer.
- OpenSSL and libffi development libraries when dependencies must be compiled.
- A network connection to the selected ACME server.

## Install from PyPI

```bash
uv pip install automatoes
```

The package installs the `manuale` and `automatoes` console scripts. The
current production workflow is exposed through `manuale`.

## Install from the repository
```bash
git clone https://github.com/candango/automatoes.git
cd automatoes
uv sync --all-extras
```

## Account and certificate workflow

Create an account once:

```bash
manuale register me@example.com
```

Authorize one or more domains:

```bash
manuale authorize example.com www.example.com
```

The command prints the DNS or HTTP challenge required by the selected method.
After the challenge is fulfilled, issue the certificate:

```bash
manuale issue --output certs example.com www.example.com
```

Revoke an issued certificate:

```bash
manuale revoke certs/example.com.crt
```

The account file contains a private key. Protect it with restrictive file
permissions and do not commit or upload it.

## Common global options

```bash
manuale --server <acme-directory> --account <account.json> --verbose \
  <command>
```

The default account path is `account.json` in the current working directory.
Use a dedicated working directory for each ACME account and certificate set.
