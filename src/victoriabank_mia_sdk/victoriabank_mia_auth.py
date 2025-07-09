"""Python SDK for Victoriabank MIA API"""

import logging
from .victoriabank_mia_sdk import VictoriabankMiaSdk, VictoriabankTokenException

logger = logging.getLogger(__name__)

class VictoriabankMiaAuthRequest:
    """Factory class responsible for creating new instances of the VictoriabankMiaAuth class."""

    @staticmethod
    def create(base_url: str = VictoriabankMiaSdk.DEFAULT_BASE_URL):
        """Creates an instance of the VictoriabankMiaAuth class."""

        client = VictoriabankMiaSdk(base_url=base_url)
        return VictoriabankMiaAuth(client)

class VictoriabankMiaAuth:
    _client: VictoriabankMiaSdk = None

    def __init__(self, client: VictoriabankMiaSdk):
        self._client = client

    def generate_token(self, username: str, password: str):
        if not username and not password:
            raise VictoriabankTokenException('Username and Password are required.')

        tokens_data = {
            'grant_type': 'password',
            'username': username,
            'password': password
        }

        return self._get_tokens(data=tokens_data)

    def refresh_token(self, refresh_token: str):
        if not refresh_token:
            raise VictoriabankTokenException('Refresh token is required.')

        tokens_data = {
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token
        }

        return self._get_tokens(data=tokens_data)

    def _get_tokens(self, data: dict):
        """Get tokens"""
        # https://test-ipspj.victoriabank.md/index.html#operations-Token-post_identity_token

        try:
            response = self._client.send_request('POST', VictoriabankMiaSdk.AUTH_TOKEN, form_data=data)
        except Exception as ex:
            logger.exception('VictoriabankMiaAuth.generate_token')
            raise VictoriabankTokenException(f'HTTP error while sending POST request to endpoint {VictoriabankMiaSdk.AUTH_TOKEN}') from ex

        result = self._client.handle_response(response, VictoriabankMiaSdk.AUTH_TOKEN)
        return result
