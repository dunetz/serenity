import base64
import hashlib
import hmac
import json
import time

from math import trunc
from typing import Tuple

from phemex import PhemexConnection, PhemexCredentials, PublicCredentials, AuthCredentials


def get_phemex_connection(credentials: PhemexCredentials = PublicCredentials(),
                          instance_id: str = 'prod') -> Tuple[PhemexConnection, str]:
    if instance_id == 'prod':
        ws_uri = 'wss://phemex.com/ws'
        return PhemexConnection(credentials), ws_uri
    elif instance_id == 'test':
        ws_uri = 'wss://testnet.phemex.com/ws'
        return PhemexConnection(credentials, api_url='https://testnet-api.phemex.com'), ws_uri
    else:
        raise ValueError(f'Unknown instance_id: {instance_id}')


class PhemexWebsocketAuthenticator:
    """
    Authentication mechanism for Phemex private WS API.
    """

    def __init__(self, credentials: AuthCredentials):
        self.api_key = credentials.api_key
        self.secret_key = credentials.secret_key

    def get_user_auth_message(self, auth_id: int = 1) -> str:
        expiry = trunc(time.time()) + 60
        token = self.api_key + str(expiry)
        token = token.encode('utf-8')
        hmac_key = base64.urlsafe_b64decode(self.secret_key)
        signature = hmac.new(hmac_key, token, hashlib.sha256)
        signature_b64 = signature.hexdigest()

        user_auth = {
            "method": "user.auth",
            "params": [
                "API",
                self.api_key,
                signature_b64,
                expiry
            ],
            "id": auth_id
        }
        return json.dumps(user_auth)
