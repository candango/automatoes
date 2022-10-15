# -*- coding: UTF-8 -*-
#
# Copyright 2019-2022 Flávio Gonçalves Garcia
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

from . import get_version
from peasant import get_version as peasant_get_version
from peasant.client import Peasant, PeasantTransport
import requests
from urllib.parse import urljoin, urlparse


class AcmeV2RequestsTransport(PeasantTransport):

    def __init__(self):
        super().__init__()
        self._directory = None
        self._user_agent = ("Automat-o-es %s Peasant %s" % (
            get_version(), peasant_get_version()))

    @property
    def DEFAULT_HEADERS(self) -> dict:
        return {'User-Agent': self._user_agent}

    def set_directory(self):
        response = self.get("/%s" % self.peasant.directory_path)
        if response.status_code == 200:
            self.peasant.directory_cache = response.json()
        else:
            raise Exception

    def new_nonce(self):
        """ Returns a new nonce """
        return self.head(self.peasant.directory['newNonce'], headers={
            'resource': "new-reg",
            'payload': None,
        }).headers.get('Replay-Nonce')

    def get(self, path, **kwargs):
        kwargs = self.create_kwargs(**kwargs)
        return requests.get(self.sanatize_path(path), **kwargs)

    def head(self, path, **kwargs):
        kwargs = self.create_kwargs(**kwargs)
        return requests.head(self.path(path), **kwargs)

    def create_kwargs(self, **kwargs):
        _headers = self.DEFAULT_HEADERS.copy()
        headers = kwargs.get("headers")
        if headers:
            _headers.update(headers)
        kwargs = {
            'headers': _headers
        }
        if self.peasant.verify:
            kwargs['verify'] = self.peasant.verify
        return kwargs

    def sanatize_path(self, path):
        """ Handle path and make it sure the right path will be used combined
        with the url from set to the peasant.
        """
        # If https is in we assume that was returned by the directory
        if path.startswith("https"):
            return path
        # Make sure path is relative
        if path.startswith("http"):
            path = urlparse(path).path
        url_parsed = urlparse(self.peasant.url)
        if url_parsed.path != "":
            url_parsed_path = url_parsed.path
            if url_parsed_path.startswith("/"):
                url_parsed_path = url_parsed_path[1:]
            if path.startswith("/"):
                path = path[1:]
            path = "%s/%s" % (url_parsed_path, path)
        return urljoin(self.peasant.url, path)


class AcmeProtocol(Peasant):

    def __init__(self, transport, **kwargs):
        super().__init__(transport)
        self._url = kwargs.get("url")
        self._account = kwargs.get("account")
        self._directory_path = kwargs.get("directory", "directory")
        self._verify = kwargs.get("verify")

    @property
    def url(self):
        return self._url

    @property
    def account(self):
        return self.account

    @account.setter
    def account(self, account):
        # TODO: Throw an error right here if account is None
        self._account = account

    @property
    def directory_path(self):
        return self._directory_path

    @directory_path.setter
    def directory_path(self, path):
        self._directory_path = path

    @property
    def verify(self):
        return self._verify
