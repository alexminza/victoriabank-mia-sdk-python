"""Python SDK for Victoriabank MIA API"""

import logging
from cryptography.x509 import load_pem_x509_certificate

import httpx
import jwt

logger = logging.getLogger(__name__)


# Based on Python SDK for maib MIA API https://github.com/alexminza/maib-mia-sdk-python (https://pypi.org/project/maib-mia-sdk/)
# IPS Business WebApi https://test-ipspj.victoriabank.md
# IPS DemoPay WebApi https://test-ipspj-demopay.victoriabank.md/swagger/

class VictoriabankMiaSdk:
    # Victoriabank MIA API base urls
    DEFAULT_BASE_URL = 'https://ips-api-pj.vb.md/'
    TEST_BASE_URL = 'https://test-ipspj.victoriabank.md/'
    TEST_DEMOPAY_URL = 'https://test-ipspj-demopay.victoriabank.md/api/pay/'

    HEALTH_STATUS = 'api/v1/health/status'
    AUTH_TOKEN = 'identity/token'

    # Victoriabank MIA API endpoints
    MIA_QR = 'api/v1/qr'
    MIA_QR_ID = 'api/v1/qr/{id}'
    MIA_QR_STATUS = 'api/v1/qr/{id}/status'
    MIA_QR_EXTENSIONS = 'api/v1/qr/{id}/extentions'
    MIA_QR_ACTIVE_EXTENSION = 'api/v1/qr/{id}/active-extension'
    MIA_QR_EXTENSION_STATUS = 'api/v1/qr-extensions/{id}/status'
    MIA_QR_EXTENSION_SIGNAL = 'api/v1/signal/{id}/'

    MIA_TRANSACTION_ID = 'api/v1/transaction/{id}'
    MIA_TRANSACTIONS_LIST = 'api/v1/reconciliation/transactions'

    DEFAULT_TIMEOUT = 30

    _base_url: str = None

    def __init__(self, base_url: str = DEFAULT_BASE_URL):
        self._base_url = base_url

    def _build_url(self, url: str, entity_id: str = None):
        """Build the complete URL for the request"""

        if not url.startswith('https://'):
            url = self._base_url + url

        if entity_id:
            url = url.format(id=entity_id)

        return url

    def _process_response(self, response: httpx.Response):
        if response.is_error:
            logger.error('%s Error: %d %s', VictoriabankMiaSdk.__qualname__, response.status_code, response.text, extra={'method': response.request.method, 'url': response.request.url, 'params': response.request.url.params, 'response_text': response.text, 'status_code': response.status_code})
            #response.raise_for_status()

        if not response.content:
            logger.debug('%s Response: %d', VictoriabankMiaSdk.__qualname__, response.status_code, extra={'response_content': response.content})
            return {}

        response_json: dict = response.json()
        logger.debug('%s Response: %d', VictoriabankMiaSdk.__qualname__, response.status_code, extra={'response_json': response_json})
        return response_json

    def send_request(self, method: str, url: str, form_data: dict = None, json_data: dict = None, params: dict = None, token: str = None, entity_id: str = None):
        """Send a request and parse the response."""

        auth = BearerAuth(token) if token else None
        url = self._build_url(url=url, entity_id=entity_id)

        logger.debug('%s Request: %s %s', VictoriabankMiaSdk.__qualname__, method, url, extra={'method': method, 'url': url, 'form_data': form_data, 'json_data': json_data, 'params': params, 'token': token})
        with httpx.Client() as client:
            response = client.request(method=method, url=url, params=params, data=form_data, json=json_data, auth=auth, timeout=self.DEFAULT_TIMEOUT)
            return self._process_response(response=response)

    async def send_request_async(self, method: str, url: str, form_data: dict = None, json_data: dict = None, params: dict = None, token: str = None, entity_id: str = None):
        """Send async request and parse the response."""

        auth = BearerAuth(token) if token else None
        url = self._build_url(url=url, entity_id=entity_id)

        logger.debug('%s Request: %s %s', VictoriabankMiaSdk.__qualname__, method, url, extra={'method': method, 'url': url, 'form_data': form_data, 'json_data': json_data, 'params': params, 'token': token})
        async with httpx.AsyncClient() as client:
            response = await client.request(method=method, url=url, params=params, data=form_data, json=json_data, auth=auth, timeout=self.DEFAULT_TIMEOUT)
            return self._process_response(response=response)

    @staticmethod
    def handle_response(response: dict, endpoint: str):
        """Handles errors returned by the API."""

        if not isinstance(response, dict):
            raise VictoriabankMiaPaymentException(f"Invalid response received from server for endpoint {endpoint}")

        error_code = response.get('errorCode')
        if error_code:
            error_description = response.get('description')
            raise VictoriabankMiaPaymentException(f'Error sending request to endpoint {endpoint}: {error_description} ({error_code})')

        return response

    @staticmethod
    def decode_callback(callback_jwt: str, public_key_pem: bytes):
        """Decodes and validates the callback data signature."""

        public_key_cert = load_pem_x509_certificate(public_key_pem)
        public_key = public_key_cert.public_key()

        algorithm = 'RS256'
        try:
            decoded_payload: dict = jwt.decode(
                jwt=callback_jwt,
                key=public_key,
                algorithms=[algorithm])

            return decoded_payload
        except Exception as ex:
            raise VictoriabankMiaPaymentException(f'Failed to decode and verify payload signature: {ex}') from ex

#region Auth
class BearerAuth(httpx.Auth):
    """Attaches HTTP Bearer Token Authentication to the given Request object."""
    # https://www.python-httpx.org/advanced/authentication/#custom-authentication-schemes

    token: str = None

    def __init__(self, token: str):
        self.token = token

    def auth_flow(self, request: httpx.Request):
        request.headers['Authorization'] = f'Bearer {self.token}'
        yield request
#endregion

#region Exceptions
class VictoriabankMiaTokenException(Exception):
    pass

class VictoriabankMiaPaymentException(Exception):
    pass
#endregion
