"""Python SDK for Victoriabank MIA API"""

import logging
from .victoriabank_mia_sdk import VictoriabankMiaSdk, VictoriabankPaymentException

logger = logging.getLogger(__name__)

class VictoriabankMiaApiRequest:
    """Factory class responsible for creating new instances of the VictoriabankMiaApi class."""

    @staticmethod
    def create(base_url: str = VictoriabankMiaSdk.DEFAULT_BASE_URL):
        """Creates a new instance of VictoriabankMiaApi."""

        client = VictoriabankMiaSdk(base_url=base_url)
        return VictoriabankMiaApi(client)

class VictoriabankMiaApi:
    _client: VictoriabankMiaSdk = None

    REQUIRED_QR_PARAMS = ['header', 'extension']
    REQUIRED_TEST_PAY_PARAMS = ['qrHeaderUUID']

    def __init__(self, client: VictoriabankMiaSdk):
        self._client = client

    #region QR
    def qr_create(self, data: dict, token: str, params: dict = None):
        """CreatePayeeQr - Register new payee-presented QR code"""
        # https://test-ipspj.victoriabank.md/index.html#operations-Qr-post_api_v1_qr

        return self._execute_operation(endpoint=VictoriabankMiaSdk.MIA_QR, data=data, token=token, required_params=self.REQUIRED_QR_PARAMS, params=params)

    def qr_status(self, qr_id: str, token: str, params: dict = None):
        """getPayeeQrStatus - Get status of payee-presented QR code header, statuses of N last extensions and list of M last payments against each extension"""
        # https://test-ipspj.victoriabank.md/index.html#operations-Qr-get_api_v1_qr__qrHeaderUUID__status

        return self._execute_entity_id_operation(endpoint=VictoriabankMiaSdk.MIA_QR_STATUS, entity_id=qr_id, token=token, params=params)

    def qr_cancel(self, qr_id: str, token: str):
        """CancelPayeeQr-Cancel payee-resented QR code, including active extension, if exists"""
        # https://test-ipspj.victoriabank.md/index.html#operations-Qr-delete_api_v1_qr__qrHeaderUUID_

        return self._execute_entity_id_operation(endpoint=VictoriabankMiaSdk.MIA_QR_ID, entity_id=qr_id, token=token, method='DELETE')
    #endregion

    #region QR Extensions
    def qr_create_extension(self, qr_id: str, data: dict, token: str):
        """CreatePayeeQrExtention - Register new extension for HYBR or STAT payee-presented QR code"""
        # https://test-ipspj.victoriabank.md/index.html#operations-Qr-post_api_v1_qr__qrHeaderUUID__extentions

        return self._execute_entity_id_operation(endpoint=VictoriabankMiaSdk.MIA_QR_EXTENSIONS, entity_id=qr_id, token=token, method='POST', data=data)

    def qr_cancel_extension(self, qr_id: str, token: str):
        """CancelHybrExtention - Cancel active extension of hybrid payee-presented QR code"""
        # https://test-ipspj.victoriabank.md/index.html#operations-Qr-delete_api_v1_qr__qrHeaderUUID__active_extension

        return self._execute_entity_id_operation(endpoint=VictoriabankMiaSdk.MIA_QR_ACTIVE_EXTENSION, entity_id=qr_id, token=token, method='DELETE')

    def qr_extension_status(self, qr_extension_id: str, token: str,  params: dict = None):
        """getQrExtensionStatus - Get status of QR code extension and list of last N payments against it"""
        # https://test-ipspj.victoriabank.md/index.html#operations-Qr-get_api_v1_qr_extensions__qrExtensionUUID__status

        return self._execute_entity_id_operation(endpoint=VictoriabankMiaSdk.MIA_QR_EXTENSION_STATUS, entity_id=qr_extension_id, token=token, params=params)
    #endregion

    #region Transactions
    def transaction_reverse(self, transaction_id: str, token: str):
        """Reverse already processed transaction"""
        # https://test-ipspj.victoriabank.md/index.html#operations-Transaction-delete_api_v1_transaction__id_

        return self._execute_entity_id_operation(endpoint=VictoriabankMiaSdk.MIA_TRANSACTION_ID, entity_id=transaction_id, token=token, method='DELETE')

    def transactions_list(self, params: dict, token: str):
        """Transaction list for reconciliation"""
        # https://test-ipspj.victoriabank.md/index.html#operations-Reconciliation-get_api_v1_reconciliation_transactions

        return self._execute_operation(endpoint=VictoriabankMiaSdk.MIA_TRANSACTIONS_LIST, data=None, token=token, required_params=None, method='GET', params=params)
    #endregion

    #region Signal
    def signal_get(self, qr_extension_id: str, token: str):
        # https://test-ipspj.victoriabank.md/index.html#operations-Signal-get_api_v1_signal__qrExtensionUUID_

        return self._execute_entity_id_operation(endpoint=VictoriabankMiaSdk.MIA_QR_EXTENSION_SIGNAL, entity_id=qr_extension_id, token=token)

    #endregion

    #region Payment
    def test_pay(self, data: dict, token: str):
        """This API enables payment simulation based on the qrHeaderUUID, without requiring any bank or financial institution applications."""
        # https://test-ipspj-demopay.victoriabank.md/swagger/index.html#operations-Pay-post_api_Pay

        return self._execute_operation(endpoint=VictoriabankMiaSdk.SANDBOX_DEMOPAY_URL, data=data, token=token, required_params=self.REQUIRED_TEST_PAY_PARAMS)
    #endregion

    def health_status(self):
        # https://test-ipspj.victoriabank.md/index.html#operations-Health-get_api_v1_health_status

        return self._send_request(method='GET', endpoint=VictoriabankMiaSdk.HEALTH_STATUS, token=None)

    def _execute_operation(self, endpoint: str, data: dict, token: str, required_params: list, method: str = 'POST', params: dict = None):
        self._validate_params(data=data, required_params=required_params)
        self._validate_access_token(token=token)
        return self._send_request(method=method, endpoint=endpoint, data=data, params=params, token=token)

    def _execute_entity_id_operation(self, endpoint: str, entity_id: str, token: str, method: str = 'GET', data: dict = None, params: dict = None):
        self._validate_id_param(entity_id=entity_id)
        self._validate_access_token(token=token)
        return self._send_request(method=method, endpoint=endpoint, token=token, data=data, params=params, entity_id=entity_id)

    def _send_request(self, method: str, endpoint: str, token: str, data: dict = None, params: dict = None, entity_id: str = None):
        """Sends a request to the specified endpoint."""

        try:
            response = self._client.send_request(method=method, url=endpoint, json_data=data, params=params, token=token, entity_id=entity_id)
        except Exception as ex:
            raise VictoriabankPaymentException(f'HTTP error while sending {method} request to endpoint {endpoint}: {ex}') from ex

        return self._client.handle_response(response, endpoint)

    @staticmethod
    def _validate_access_token(token: str):
        """Validates the access token."""

        if not token or len(token) == 0:
            raise VictoriabankPaymentException('Access token is not valid. It should be a non-empty string.')

    @staticmethod
    def _validate_id_param(entity_id: str):
        """Validates the ID parameter."""

        if not entity_id:
            raise VictoriabankPaymentException('Missing ID.')

        if len(entity_id) == 0:
            raise VictoriabankPaymentException('Invalid ID parameter. Should be string of 36 characters.')

    @staticmethod
    def _validate_params(data: dict, required_params: list):
        """Validates the parameters."""

        if data and required_params:
            # Check that all required parameters are present
            for param in required_params:
                if data.get(param) is None:
                    raise VictoriabankPaymentException(f'Missing required parameter: {param}')

        return True
