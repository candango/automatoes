Features
========

* Simple interface with no hoops to jump through. Keys and certificate signing
requests are automatically generated: no more cryptic OpenSSL one-liners.
(However, you do need to know what to do with generated certificates and keys
yourself!)

* Support for DNS & HTTP validation. No need to figure out how to serve
challenge files from a live domain.

* Obviously, runs without root access. Use it from any machine you want, it
doesn't care. Internet connection recommended.

* Awful, undiscoverable name.

* And finally, if the `openssl` binary is your spirit animal after all, you can
still bring your own keys and/or CSR's. Everybody wins.