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
from automatoes.errors import AccountAlreadyExistsError, AcmeError
from automatoes.model import Account, RegistrationResult

from peasant.client.protocol import Peasant
from peasant.client.transport import METHOD_POST
from peasant.client.transport_requests import RequestsTransport


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


class AcmeRequestsTransport(RequestsTransport):

    peasant: AcmeV2Pesant

    def __init__(self, bastion_address):
        super().__init__(bastion_address)
        self._directory = None
        self.user_agent = (f"Automatoes/{get_version()} {self.user_agent}")
        self.basic_headers = {
            'User-Agent': self.user_agent
        }
        self.kwargs_updater = self.update_kwargs

    def update_kwargs(self, method, **kwargs):
        if self.peasant.verify:
            kwargs['verify'] = self.peasant.verify
        return kwargs

    def set_directory(self):
        response = self.get("/%s" % self.peasant.directory_path)
        if response.status_code == 200:
            self.peasant.directory_cache = response.json()
        else:
            raise Exception

    def new_nonce(self):
        """ Return a new nonce """
        return self.head(self.peasant.directory()['newNonce'], headers={
            'resource': "new-reg",
            'payload': None,
        }).headers.get('Replay-Nonce')

    def new_account(self, account: Account, contacts: list,
                    terms_agreed: bool = False):
        """ Create a new account in the Acme Server """
        payload = {
           "termsOfServiceAgreed": terms_agreed,
           "contact": [f"mailto:{contact}" for contact in contacts],
        }
        response = self.post(
            self.peasant.directory()['newAccount'],
            payload
        )

        uri = response.headers.get("Location")

        if response.status_code == 201:
            self.account.uri = uri

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


def _json(response):
    try:
        return response.json()
    except ValueError as e:
        raise AcmeError("Invalid JSON response. {}".format(e))
