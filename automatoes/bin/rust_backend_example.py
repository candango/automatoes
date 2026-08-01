import rust_backend

try:
    nonce = rust_backend.new_nonce(
        "https://localhost:14000/nonce-plz",
        "tests/certs/candango.minica.pem",
    )
    print(nonce)
except rust_backend.MariolaError as error:
    print(f"Falha ao obter nonce: {error}")


print(rust_backend.hello("Automatoes"))
print(rust_backend.add(20, 22))
