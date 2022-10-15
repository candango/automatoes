#!/usr/bin/env python
#
# Copyright 2019-2022 Flávio Gonçalves Garcia
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


import json

from .crypto import (generate_jwk_thumbprint, load_private_key,
                     export_private_key)
from datetime import datetime


class Account:

    def __init__(self, key, uri=None):
        self.key = key
        self.uri = uri

    def serialize(self):
        return json.dumps({
            'key': export_private_key(self.key).decode("utf-8"),
            'uri': self.uri,
        }).encode("utf-8")

    @property
    def thumbprint(self):
        return generate_jwk_thumbprint(self.key)

    @staticmethod
    def deserialize(data):
        try:
            if not isinstance(data, str):
                data = data.decode('utf-8')
            data = json.loads(data)
            if "key" not in data or "uri" not in data:
                raise ValueError("Missing 'key' or 'uri' fields.")
            return Account(key=load_private_key(data['key'].encode("utf8")),
                           uri=data['uri'])
        except (TypeError, ValueError, AttributeError) as e:
            raise IOError("Invalid account structure: {}".format(e))


class Authorization:

    def __init__(self, contents, uri, ty_pe):
        self.contents = contents
        self.uri = uri
        self.type = ty_pe
        self.certificate_uri = None
        self.certificate = {}


class Challenge:

    def __init__(self, contents, domain, expires, status, ty_pe, key):
        self.contents = contents
        self.domain = domain
        self.expires = expires
        self.status = status
        self.type = ty_pe
        self.key = key

    def serialize(self):
        return json.dumps({
            'contents': self.contents,
            'domain': self.domain,
            'expires': self.expires,
            'status': self.status,
            'type': self.type,
            'key': self.key
        }).encode('utf-8')

    @property
    def file_name(self):
        return "{}_challenge.json".format(self.domain)


class Order:

    def __init__(self, contents, uri, ty_pe):
        self.contents = contents
        self.uri = uri
        self.type = ty_pe
        self.certificate_uri = None
        self.certificate = {}
        self.key = None

    @property
    def expired(self):
        if self.contents['status'] == "expired":
            return True
        order_timestamp = datetime.strptime(self.contents['expires'][0:19],
                                            "%Y-%m-%dT%H:%M:%S")
        return order_timestamp < datetime.now()

    @property
    def invalid(self):
        return self.contents['status'] == "invalid"

    def serialize(self):
        return json.dumps({
            'contents': self.contents,
            'uri': self.uri,
            'type': self.type,
            'certificate_uri': self.certificate_uri,
            'key': self.key
        }).encode("utf-8")

    @staticmethod
    def deserialize(data):
        try:
            if not isinstance(data, str):
                data = data.decode("utf-8")
            data = json.loads(data)
            if 'contents' not in data:
                raise ValueError("Missing 'contents' field.")
            if 'uri' not in data:
                raise ValueError("Missing 'uri' field.")
            if 'type' not in data:
                raise ValueError("Missing 'type' field.")
            order = Order(contents=data['contents'],
                          uri=data['uri'],
                          ty_pe=data['type'])
            if data['certificate_uri']:
                order.certificate_uri = data['certificate_uri']
            if data['key']:
                order.key = data['key']
            return order
        except (TypeError, ValueError, AttributeError) as e:
            raise IOError("Invalid account structure: {}".format(e))
