#!/usr/bin/env python
#
# Copyright 2019 Flavio Garcia
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
A small container for account data. Ideally we would get away with just using a
PEM-encoded RSA private key as the account file, but we might need the account
URI at some point.
"""

import json

from .crypto import load_private_key, export_private_key


class Account:

    def __init__(self, key, uri=None):
        self.key = key
        self.uri = uri

    def serialize(self):
        return json.dumps({
            'key': export_private_key(self.key).decode('utf-8'),
            'uri': self.uri,
        }).encode('utf-8')


def deserialize(data):
    try:
        if not isinstance(data, str):
            data = data.decode('utf-8')
        data = json.loads(data)
        if 'key' not in data or 'uri' not in data:
            raise ValueError("Missing 'key' or 'uri' fields.")
        return Account(key=load_private_key(data['key'].encode('utf8')),
                       uri=data['uri'])
    except (TypeError, ValueError, AttributeError) as e:
        raise IOError("Invalid account structure: {}".format(e))
