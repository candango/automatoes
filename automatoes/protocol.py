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
from automatoes.model import Account, RegistrationResult

import copy

from peasant.client.protocol import Peasant
from peasant.client.transport import METHOD_POST
from peasant.client.transport_requests import RequestsTransport

import requests


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

    def get_registration(self, account: Account):
        return self.transport.get_registration(account)

    def new_account(self, account: Account, contacts: list,
                    terms_agreed: bool = False) -> RegistrationResult:
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
            if data:
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
        """Send a POST request.

        :param path: absolute or relative URL for the new
        :class:`requests.Request` object.
        :param **kwargs: Optional arguments that ``request`` takes.
        :return: :class:`requests.Response <Response>` object
        :rtype: requests.Response
        """
        url = self.get_url(path, **kwargs)
        headers = self.get_headers(**kwargs)
        kwargs['headers'] = headers
        kwargs = self.update_kwargs(METHOD_POST, **kwargs)
        with requests.post(url, **kwargs) as result:
            result.raise_for_status()
        return result

    def set_directory(self):
        response = self.get("/%s" % self.peasant.directory_path)
        if response.status_code == 200:
            self.peasant.directory_cache = response.json()
        else:
            raise Exception

    def get_registration(self, account: Account):
        """
        Get available account information from the server.
        """
        headers = {'Content-Type': "application/jose+json"}
        response = self.post_as_get(account.uri, headers=headers,
                                    kid=self.account.uri,
                                    key=account.key, uri=account.uri)
        if str(response.status_code).startswith("2"):
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
                    terms_agreed: bool = False) -> RegistrationResult:
        """ Create a new account in the Acme Server """
        payload = {
           "termsOfServiceAgreed": terms_agreed,
           "contact": [f"mailto:{contact}" for contact in contacts],
        }
        headers = {'Content-Type': "application/jose+json"}
        path = self.peasant.directory()['newAccount']
        response = self.post_as_get(path, data=payload, headers=headers,
                                    key=account.key, uri=path)

        uri = response.headers.get("Location")

        if response.status_code == 201:
            # Find terms of service from link headers
            terms = self.terms_from_directory()
            return RegistrationResult(
                contents=_json(response),
                uri=uri,
                terms=terms
            )
        elif response.status_code == 409:
            raise AccountAlreadyExistsError(response, uri)
        raise AcmeError(response)

    def terms_from_directory(self):
        response = self.get_directory()
        if response.status_code == 200:
            if "meta" in response.json():
                if "termsOfService" in response.json()['meta']:
                    return response.json()['meta']['termsOfService']
        return None


def _json(response):
    try:
        return response.json()
    except ValueError as e:
        raise AcmeError("Invalid JSON response. {}".format(e))
