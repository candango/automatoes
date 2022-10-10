# -*- coding: UTF-8 -*-
#
# Copyright 2019-2020 Flavio Garcia
# Copyright 2016-2017 Veeti Paananen under MIT License
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

"""
Cryptography, hopefully mostly correct.
"""

import base64
import json
import logging
# TODO: Remove that after python 3.5 depreciation
import warnings
with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    from cryptography import x509
from cryptography.x509 import NameOID
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.asymmetric.rsa import (
    generate_private_key,
    RSAPrivateKey,
)
from cryptography.hazmat.primitives.asymmetric.ec import (
    EllipticCurvePrivateKey,
)
from cryptography.hazmat.primitives.serialization import (
    load_pem_private_key,
    Encoding,
    PrivateFormat,
    NoEncryption,
)
from cryptography.hazmat.primitives import hashes

import re

logger = logging.getLogger(__name__)


def jose_b64(data):
    """
    Encodes data with JOSE/JWS base 64 encoding.
    """
    return base64.urlsafe_b64encode(data).decode('ascii').replace('=', '')


def generate_rsa_key(size=2048):
    """
    Generates a new RSA private key.
    """
    return generate_private_key(65537, size, default_backend())


def generate_header(account_key):
    """
    Creates a new request header for the specified account key.
    """
    numbers = account_key.public_key().public_numbers()
    e = numbers.e.to_bytes((numbers.e.bit_length() // 8 + 1), byteorder='big')
    n = numbers.n.to_bytes((numbers.n.bit_length() // 8 + 1), byteorder='big')
    if n[0] == 0: # for strict JWK
        n = n[1:]
    return {
        'alg': 'RS256',
        'jwk': {
            'kty': 'RSA',
            'e': jose_b64(e),
            'n': jose_b64(n),
        },
    }


def generate_jwk_thumbprint(account_key):
    """
    Generates a JWK thumbprint for the specified account key.
    """
    jwk = generate_header(account_key)['jwk']
    as_json = json.dumps(jwk, sort_keys=True, separators=(',', ':'))

    sha256 = hashes.Hash(hashes.SHA256(), default_backend())
    sha256.update(as_json.encode('utf-8'))

    return jose_b64(sha256.finalize())


def sign_request(key, header, protected_header, payload):
    """
    Creates a JSON Web Signature for the request header and payload using the
    specified account key.
    """
    protected = jose_b64(json.dumps(protected_header).encode('utf8'))
    payload = jose_b64(json.dumps(payload).encode('utf8'))
    data = "{%s}.{%s}" % (protected, payload)
    signed_data = key.sign(data.encode("ascii"), padding.PKCS1v15(),
                           hashes.SHA256())
    return json.dumps({
        'header': header,
        'protected': protected,
        'payload': payload,
        'signature': jose_b64(signed_data),
    })


def sign_request_v2(key, protected_header, payload):
    """
    Creates a JSON Web Signature for the request header and payload using the
    specified account key.
    """
    protected = jose_b64(json.dumps(protected_header).encode('utf8'))
    # Forced payload none for Post-as-Get
    if payload is not None and payload != "":
        payload = jose_b64(json.dumps(payload).encode('utf8'))
    elif payload is None:
        payload = ""
    data = "{protected}.{payload}".format(protected=protected, payload=payload)
    signed_data = key.sign(data.encode("ascii"), padding.PKCS1v15(),
                           hashes.SHA256())
    return json.dumps({
        'protected': protected,
        'payload': payload,
        'signature': jose_b64(signed_data),
    })


def load_private_key(data):
    """
    Loads a PEM-encoded private key.
    """
    key = load_pem_private_key(data, password=None, backend=default_backend())
    if not isinstance(key, (RSAPrivateKey, EllipticCurvePrivateKey)):
        raise ValueError("Key is not a private RSA or EC key.")
    elif isinstance(key, RSAPrivateKey) and key.key_size < 2048:
        raise ValueError("The key must be 2048 bits or longer.")

    return key


def export_private_key(key):
    """
    Exports a private key in OpenSSL PEM format.
    """
    return key.private_bytes(Encoding.PEM, PrivateFormat.TraditionalOpenSSL, NoEncryption())


def create_csr(key, domains, must_staple=False):
    """
    Creates a CSR in DER format for the specified key and domain names.
    """
    assert domains
    name = x509.Name([
        x509.NameAttribute(NameOID.COMMON_NAME, domains[0]),
    ])
    san = x509.SubjectAlternativeName(
        [x509.DNSName(domain) for domain in domains])
    csr = (x509.CertificateSigningRequestBuilder()
           .subject_name(name).add_extension(san, critical=False))
    if must_staple:
        ocsp_must_staple = x509.TLSFeature(
            features=[x509.TLSFeatureType.status_request])
        csr = csr.add_extension(ocsp_must_staple, critical=False)
    return csr.sign(key, hashes.SHA256(), default_backend())


def export_csr_for_acme(csr):
    """
    Exports a X.509 CSR for the ACME protocol (JOSE Base64 DER).
    """
    return export_certificate_for_acme(csr)


def load_csr(data):
    """
    Loads a PEM X.509 CSR.
    """
    return x509.load_pem_x509_csr(data, default_backend())


def load_der_certificate(data):
    """
    Loads a DER X.509 certificate.
    """
    return x509.load_der_x509_certificate(data, default_backend())


def load_pem_certificate(data):
    """
    Loads a PEM X.509 certificate.
    """
    return x509.load_pem_x509_certificate(data, default_backend())


def get_certificate_domain_name(cert):
    return cert.subject.get_attributes_for_oid(NameOID.COMMON_NAME)[0].value


def get_certificate_domains(cert):
    """
    Gets a list of all Subject Alternative Names in the specified certificate.
    """
    for ext in cert.extensions:
        ext = ext.value
        if isinstance(ext, x509.SubjectAlternativeName):
            return ext.get_values_for_type(x509.DNSName)
    return []


def export_pem_certificate(cert):
    """
    Exports a X.509 certificate as PEM.
    """
    return cert.public_bytes(Encoding.PEM)


def export_certificate_for_acme(cert):
    """
    Exports a X.509 certificate for the ACME protocol (JOSE Base64 DER).
    """
    return jose_b64(cert.public_bytes(Encoding.DER))


def strip_certificates(data):
    p = re.compile("-----BEGIN CERTIFICATE-----\n(?s).+?"
                   "-----END CERTIFICATE-----\n")
    stripped_data = []
    for cert in p.findall(data.decode()):
        stripped_data.append(cert.encode())
    return stripped_data
