# CLI reference

The supported manual workflow is implemented by `manuale`.

## `register`

Create and register an ACME account.

```bash
manuale register EMAIL [--key-file PATH]
```

If `--key-file` is omitted, a new RSA account key is generated. The resulting
account is serialized to the configured account path.

## `authorize`

Create or resume an ACME order and fulfill domain challenges.

```bash
manuale authorize DOMAIN [DOMAIN ...] [--method {dns,http}]
```

DNS is the default method. Order state and challenge data are persisted so an
interrupted workflow can resume.

## `issue`

Finalize an authorized order and download its certificate.

```bash
manuale issue DOMAIN [DOMAIN ...] \
  [--key-size BITS] [--key-file PATH] [--csr-file PATH] \
  [--output DIRECTORY] [--output-filename NAME] \
  [--ocsp-must-staple]
```

The command writes the private key, leaf certificate, full chain, and
intermediate certificate to the output directory.

## `revoke`

Revoke a certificate using the account associated with the current workflow.

```bash
manuale revoke CERTIFICATE
```

## `info`

Display account information retrieved from the ACME server.

```bash
manuale info
```

## `upgrade`

Upgrade a production Let's Encrypt ACME V1 account URI to ACME V2 after
confirmation.

```bash
manuale upgrade
```

## `migrate`

Convert a Certbot account directory into an Automatoes account file.

```bash
manuale migrate --certbot-path PATH
```

The source directory must contain `private_key.json` and `regr.json`.

## `version`

Show the installed version:

```bash
manuale version
```

The `automatoes` command remains a compatibility entry point; its newer
automated workflow is not implemented yet.
