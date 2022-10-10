#!/bin/bash
##
## Copyright 2019-2022 Flavio Gonçalves Garcia
##
## Licensed under the Apache License, Version 2.0 (the "License");
## you may not use this file except in compliance with the License.
## You may obtain a copy of the License at
##
##    http://www.apache.org/licenses/LICENSE-2.0
##
## Unless required by applicable law or agreed to in writing, software
## distributed under the License is distributed on an "AS IS" BASIS,
## WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
## See the License for the specific language governing permissions and
## limitations under the License.
##
## install_service.sh    Install peeble, minica and generates minica keys for
##                       a localhost instance of peeble be certified for tests.
##
## description: Peeble service runner.
## processname: install_service.sh
##
## Author: Flavio Garcia <piraz@candango.org>

OK_STRING="[ \033[32mOK\033[37m ]"

echo "Installing Peeble: "
git clone git@github.com:letsencrypt/pebble.git
cd pebble
go install ./cmd/pebble
cd -
rm -rf pebble
echo -e "Peeble installed .......... $OK_STRING"
echo -n "Installing Minica ........ "
go install github.com/jsha/minica@latest
echo -e " $OK_STRING"
echo -n "Generating minica keys ... "
rm -rf tests/certs/*.pem tests/certs/localhost
cd tests/certs
"$GOPATH"/bin/minica -domains localhost -ca-cert candango.minica.pem -ca-key candango.minica.key.pem
cd - > /dev/null
echo -e " $OK_STRING"
