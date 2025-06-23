# Copyright 2019-2025 Flavio Garcia
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

from automatoes import get_version
from automatoes.crypto import generate_protected_header, sign_request_v2
from automatoes.errors import AccountAlreadyExistsError, AcmeError
from automatoes.model import (Account, AccountResponse, RegistrationResponse)

import copy

from peasant.client.protocol import Peasant
from peasant.client.transport import METHOD_POST
from peasant.client.transport_requests import RequestsTransport

import requests
import warnings


class AcmeV2Pesant(Peasant):

    def __init__(self, transport, **kwargs):
        """
        """
        super().__init__(transport)
        self._directory_path = kwargs.get("directory", "directory")
        self._verify = kwargs.get("verify")

    @property
    def directory_path(self):
        return self._directory_path

    @directory_path.setter
    def directory_path(self, path):
        self._directory_path = path

    @property
    def verify(self):
        return self._verify

    def get_registration(self, account: Account) -> RegistrationResponse:
        return self.transport.get_registration(account)

    def new_account(self, account: Account, contacts: list,
                    terms_agreed: bool = False) -> AccountResponse:
        return self.transport.new_account(account, contacts, terms_agreed)


class AcmeRequestsTransport(RequestsTransport):

    peasant: AcmeV2Pesant

    def __init__(self, bastion_address):
        super().__init__(bastion_address)
        self._directory = None
        self.user_agent = (f"Automatoes/{get_version()} {self.user_agent}")
        self.basic_headers = {
            'User-Agent': self.user_agent
        }
        self.kwargs_updater = self.__kwargs_updater

    def __kwargs_updater(self, method, **kwargs):
        if method == METHOD_POST:
            kid = None
            if "kid" in kwargs:
                kid = kwargs.pop("kid")
            key = None
            if "key" in kwargs:
                key = kwargs.pop("key")
            uri = None
            if "uri" in kwargs:
                uri = kwargs.pop("uri")
            protected = self.get_protected_headers(key, uri=uri)
            if kid:
                protected['kid'] = kid
                protected.pop("jwk")
            data = kwargs.get("data")
            kwargs['data'] = sign_request_v2(key, protected, data)
        if self.peasant.verify:
            kwargs['verify'] = self.peasant.verify
        return kwargs

    def get_protected_headers(self, key, uri=None):
        """
        Builds a new pair of headers for signed requests.
        """
        header = generate_protected_header(key)
        protected_header = copy.deepcopy(header)
        protected_header['nonce'] = self.new_nonce()
        if uri is not None:
            protected_header['url'] = uri
        return protected_header

    def post_as_get(self, path, **kwargs):
        """Send a POST as GET request.

        This method enforces no data/body being passed into kwargs.

        If either data or body is present into kwargs a warning will be
        displayed and the value will be discarded.

        This post will be sent without body into.

        :param path: absolute or relative URL for the new
        :class:`requests.Request` object.
        :param **kwargs: Optional arguments that ``request`` takes.
        :return: :class:`requests.Response <Response>` object
        :rtype: requests.Response
        """
        if "data" in kwargs:
            kwargs.pop("data")
            warnings.warn("Do not pass the key 'data' in kwargs. The "
                          "post_as_get method won't add body to the request "
                          "and the value will be ignored!",
                          category=RuntimeWarning)
        if "body" in kwargs:
            kwargs.pop("body")
            warnings.warn("Do not pass the key 'body' in kwargs. The "
                          "post_as_get method won't add body to the request "
                          "and the value will be ignored!",
                          category=RuntimeWarning)
        return self.post(path, **kwargs)

    def set_directory(self):
        response = self.get("/%s" % self.peasant.directory_path)
        if response.status_code == 200:
            self.peasant.directory_cache = response.json()
        else:
            raise Exception

    def get_registration(self, account: Account) -> RegistrationResponse:
        """
        Get available account information from the server.
        """
        headers = {'Content-Type': "application/jose+json"}
        response = self.post_as_get(account.uri, headers=headers,
                                    kid=account.uri, key=account.key,
                                    uri=account.uri)
        if str(response.status_code).startswith("2"):
            response_json = _json(response)
            return RegistrationResponse(
                contact=response_json['contact'],
                orders=response_json['orders'],
                status=response_json['status'],
            )
            return _json(response)
        raise AcmeError(response)

    def new_nonce(self):
        """ Return a new nonce """
        return self.head(self.peasant.directory()['newNonce'], headers={
            'resource': "new-reg",
            'payload': None,
        }).headers.get('Replay-Nonce')

    # TODO: Document that this method used to be called register
    def new_account(self, account: Account, contacts: list,
                    terms_agreed: bool = False) -> AccountResponse:
        """ Create a new account in the Acme Server """
        payload = {
           "termsOfServiceAgreed": terms_agreed,
           "contact": [f"mailto:{contact}" for contact in contacts],
        }
        headers = {'Content-Type': "application/jose+json"}
        path = self.peasant.directory()['newAccount']
        response = self.post(path, data=payload, headers=headers,
                             key=account.key, uri=path)
        if response.status_code == 201:
            uri = response.headers.get("Location")
            # Find terms of service from link headers
            terms = self.terms_from_directory()
            response_json = _json(response)
            account.contact = response_json['contact']
            account.orders = response_json['orders']
            account.uri = uri
            return AccountResponse(
                orders=response_json['orders'],
                status=response_json['status'],
                terms=terms,
            )
        elif response.status_code == 409:
            raise AccountAlreadyExistsError(response, uri)
        raise AcmeError(response)

    def terms_from_directory(self):
        # TODO: Check how to trigger an error here
        directory = self.peasant.directory()
        if "meta" in directory:
            if "termsOfService" in directory['meta']:
                return directory['meta']['termsOfService']
        return None


def _json(response):
    try:
        return response.json()
    except ValueError as e:
        raise AcmeError("Invalid JSON response. {}".format(e))
