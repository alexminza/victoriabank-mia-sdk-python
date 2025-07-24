# Python SDK for Victoriabank MIA API
* Victoriabank IPS Business WebApi docs: https://test-ipspj.victoriabank.md
* GitHub project https://github.com/alexminza/victoriabank-mia-sdk-python
* PyPI package https://pypi.org/project/victoriabank-mia-sdk/

## Installation
To easily install or upgrade to the latest release, use `pip`:
```shell
pip install --upgrade victoriabank-mia-sdk
```

## Getting started
Import SDK:

```python
from victoriabank_mia_sdk import VictoriabankMiaSdk, VictoriabankMiaAuthRequest, VictoriabankMiaApiRequest
```

Add project configuration:

```python
import os, datetime

VB_PUBLIC_KEY_PATH = os.getenv('VB_PUBLIC_KEY_PATH')
VB_MIA_USERNAME = os.getenv('VB_MIA_USERNAME')
VB_MIA_PASSWORD = os.getenv('VB_MIA_PASSWORD')
VB_IBAN = os.getenv('VB_IBAN')
```

## SDK usage examples
### Get Access Token with username and password

```python
vb_mia_auth = VictoriabankMiaAuthRequest \
    .create(base_url=VictoriabankMiaSdk.SANDBOX_BASE_URL) \
    .generate_token(username=VB_MIA_USERNAME, password=VB_MIA_PASSWORD)

vb_mia_token = vb_mia_auth['accessToken']
```

### Create a dynamic order payment QR

```python
vb_mia_qr_data = {
    'header': {
        'qrType': 'DYNM', # Type of QR code: DYNM - Dynamic QR, STAT - Static QR, HYBR - Hybrid QR
        'amountType': 'Fixed', # Specifies the type of amount: Fixed - Dynamic QR, Controlled - Static QR, Free - Hybrid QR
        'pmtContext': 'e' #Payment context: m - mobile payment, e - e-commerce payment, i - invoice payment, 0 - other
    },
    'extension': {
        'creditorAccount': {
            'iban': f'{VB_IBAN}' # The account from which funds will be debited credited.
        },
        'amount': {
            'sum': 123.45, # The total sum to be paid.
            'currency': 'MDL' # The currency in which the sum is specified.
        },
        'dba': 'TEST SRL', #Commercial name that will appear in client APP.
        'remittanceInfo4Payer': 'Order #123', #Payment destination.
        'creditorRef': '123', #External payment reference.
        'ttl': {
            'length': 60, #The duration for which the QR code is valid.
            'units': 'mm' #The unit of time for the TTL: ss - seconds, mm - minutes
        }
    }
}

vb_mia_api_request = VictoriabankMiaApiRequest.create(base_url=VictoriabankMiaSdk.SANDBOX_BASE_URL)
vb_mia_create_qr_response = vb_mia_api_request.qr_create(
    data=vb_mia_qr_data,
    token=vb_mia_token)
```

### Decode callback and validate signature

```python
callback_jwt = """eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJzaWduYWxDb2RlIjoiRXhwaXJhdGlvbiIsInNpZ25hbER0VG0iOiIyMDI0LTEwLTAxVDE1OjA3OjQ1KzAzOjAwIiwicXJIZWFkZXJVVUlEIjoiYmQxMjA0OWItNjUxZC00MGEwLWIyYmMtZDZhMGY3ZTJiN2M3IiwicXJFeHRlbnNpb25VVUlEIjoiNjU0YWNkNjktNjAyYy00MzUxLTk1OTItODE0M2FlMjhkM2U0IiwicGF5bWVudCI6bnVsbH0.WJ5t8jtg2_6DPrxQNIcu50gsW7cDC8IMdjvOBO9wW3toIdeAljlMPxd_lLCWJiKXToRAVHU7a1EB4mLyzyw1iCcRadnsSqm21TrpDZWTjv3uL-XiMLrWOsGBf0aJJRFcGbysU_ym9YLonQMmYLF0voq39yAPMHO7CLCniSMhVdJ9Q5xnrq52y6Yn5YzefCNb2tAQ-erm-8_mCaF0DWd0UFhPA6TRXyV2l5GCkLbyhlUB9gVoVTdSN-XxA_1aoNTusheZPDH1InL03Bx3G8muaVxOMrMIsVCJJYAaTFKiQTBf0M49oTQpdPWeeS9wHaS7aSS3gUcFsOOEPavj7J8vxg"""

with open(VB_PUBLIC_KEY_PATH, mode='rb') as vb_public_key_file:
    vb_public_key_pem = vb_public_key_file.read()

decoded_payload = VictoriabankMiaSdk.decode_callback(
    callback_jwt=callback_jwt,
    public_key_pem=vb_public_key_pem)
```

### Perform a test QR payment

```python
vb_test_pay_data = {
    'qrHeaderUUID': vb_mia_create_qr_response['qrHeaderUUID']
}

vb_test_pay_response = vb_mia_api_request.test_pay(
    data=vb_test_pay_data,
    token=vb_mia_token)
```

### Get payment details

```python
vb_qr_extension_status_response = vb_mia_api_request.qr_extension_status(
    qr_extension_id=vb_mia_create_qr_response['qrExtensionUUID'],
    token=vb_mia_token)
```

### Refund payment

```python
vb_payment_reference: str = vb_qr_extension_status_response['payments'][0]['reference']
vb_transaction_id = vb_payment_reference.split('|')[3]

vb_transaction_reverse_response = vb_mia_api_request.transaction_reverse(
    transaction_id=vb_transaction_id,
    token=vb_mia_token)
```
