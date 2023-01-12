# Copyright 2019-2023 Flávio Gonçalves Garcia
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import base64

from behave import given, when, then
from automatoes.crypto import generate_rsa_key_from_parameters
from automatoes.model import Account
import binascii
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateNumbers, RSAPublicNumbers
import json
import os
from cartola import fs


def enc(data):
    if isinstance(data, str):
        data = data.encode()
    missing_padding = 4 - len(data) % 4
    if missing_padding:
        data += b"=" * missing_padding
    return (b"0x" + binascii.hexlify(
        base64.b64decode(data, b'-_')).upper()).decode()


def certbot_key_to_int(key_data: dict):
    key_data_int = {}
    for key, value in key_data.items():
        key_data_int[key] = int(enc(value), 16)
    return key_data_int


def certbot_key_to_asn1(key_data: dict):
    return ("asn1=SEQUENCE:private_key\n[private_key]\n"
            "version=INTEGER:0\n"
            "n=INTEGER:%s\n"
            "e=INTEGER:%s\n"
            "d=INTEGER:%s\n"
            "p=INTEGER:%s\n"
            "q=INTEGER:%s\n"
            "dp=INTEGER:%s\n"
            "dq=INTEGER:%s\n"
            "qi=INTEGER:%s\n"
            % (enc(key_data['n']), enc(key_data['e']), enc(key_data['d']),
               enc(key_data['p']), enc(key_data['q']), enc(key_data['dp']),
               enc(key_data['dq']), enc(key_data['qi']))
            )


@given("We have certbot account at {certbot_path} path")
def step_v2_server_is_accessible(context, certbot_path):
    if os.path.exists(certbot_path):
        meta_path = os.path.join(certbot_path, "meta.json")
        key_path = os.path.join(certbot_path, "private_key.json")
        regr_path = os.path.join(certbot_path, "regr.json")
        meta_data = json.loads(fs.read(meta_path))
        key_data = json.loads(fs.read(key_path))
        regr_data = json.loads(fs.read(regr_path))

        print(meta_data)
        print(regr_data)




        # TODO: READ https://python-asn1.readthedocs.io/en/latest/examples.html

        asn1_key = certbot_key_to_asn1(key_data)

        # decoder = asn1.Decoder()
        # decoder.start(asn1_key.encode())
        key_data_int = certbot_key_to_int(key_data)
        private_key = generate_rsa_key_from_parameters(
            key_data_int['p'], key_data_int['q'], key_data_int['d'],
            key_data_int['dp'], key_data_int['dq'], key_data_int['qi'],
            key_data_int['e'], key_data_int['n']
        )
        account_file_path = os.path.join(
            "/home/fpiraz/source/candango/tmp/buga_huga_keys",
            "account.json"
        )
        account = Account(key=private_key, uri=regr_data['uri'])
        fs.write(account_file_path, account.serialize(), True)



        #print(public_numbers)


        #
        # private_numbers = RSAPrivateNumbers(
        #     enc(key_data['p']), enc(key_data['q']), enc(key_data['d']),
        #     enc(key_data['dp']), enc(key_data['dq']), enc(key_data['qi']),
        #     public_numbers)





        #print(cert)

        # encoder = asn1.Encoder()
        # encoder.start()
        # encoder
        # encoder.write(asn1_key.encode(), asn1.Numbers.PrintableString)
        # der_key = encoder.output()


        # while not decoder.eof():
        #     tag, value = decoder.read()
        #     print(value)
        return
    raise Exception()
