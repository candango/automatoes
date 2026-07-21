# Security

## Account keys

`account.json` contains a private RSA key. Treat it as a credential:

- Keep it outside source control and shared artifacts.
- Use restrictive permissions such as `0600`.
- Store it in a dedicated working directory.
- Back it up only through an approved encrypted mechanism.
- Never paste it into issues, logs, or support requests.

Certificate private keys generated during issuance require the same handling.

## TLS verification

Pebble uses a local development CA. Tests pass
`tests/certs/candango.minica.pem` as the Requests verification bundle. This is
CA pinning for the test server, not `verify=False` and not a TLS bypass.

The private CA key must never be used by application code or committed into
artifacts. The test helper may regenerate local server certificates when
needed.

## Test-only behavior

Pebble test variables such as `PEBBLE_VA_ALWAYS_VALID` make challenge tests
deterministic. They must not be copied into production ACME deployments.

## Migration safety

Certbot migration reads private key material from `private_key.json` and writes
a new Automatoes account file. Use a temporary or controlled destination,
verify the resulting account, and remove temporary copies after validation.

## Reporting

Report suspected credential exposure or security vulnerabilities privately to
the project maintainers before opening a public issue.
