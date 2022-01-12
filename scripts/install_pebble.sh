#!/bin/bash
echo -n "Installing Peeble ... "
go get -u github.com/letsencrypt/pebble/...
echo "[ OK ]"
echo -n "Installing Minica ... "
go install github.com/jsha/minica@latest
echo "[ OK ]"
echo -n "Generating minica keys ... "
rm -rf tests/certs/*.pem tests/certs/localhost
cd tests/certs
"$GOPATH"/bin/minica -domains localhost -ca-cert candango.minica.pem -ca-key candango.minica.key.pem
cd - > /dev/null
echo "[ OK ]"
