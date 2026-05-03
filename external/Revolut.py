import base64
import json
import logging
import time
import uuid

from external import http_client
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ed25519

from setup import IS_PROD


class RevolutApi:
    def __init__(self, private_key_pem: str, api_key: str) -> None:
        self.base_url = "https://revx.revolut.com"
        self.api_key = api_key
        self.private_key = serialization.load_pem_private_key(
            private_key_pem.encode(), password=None, backend=default_backend()
        )

    def _get_signature(self, timestamp, method, path, query="", body=""):
        message = f"{timestamp}{method}{path}{query}{body}".encode("utf-8")
        signature = self.private_key.sign(message)
        return base64.b64encode(signature).decode()

    def get_balances(self):
        if not IS_PROD:
            logging.info("REVOLUT: Mocking get_balances (Non-PROD)")
            return [{"currency": "GBP", "available": "100.00"}]

        method = "GET"
        path = "/api/1.0/balances"
        timestamp = time.time_ns() // 1_000_000
        headers = {
            "Accept": "application/json",
            "X-Revx-API-Key": self.api_key,
            "X-Revx-Timestamp": str(timestamp),
            "X-Revx-Signature": self._get_signature(timestamp, method, path, "", ""),
        }
        try:
            response = http_client.request(
                method, f"{self.base_url}{path}", headers=headers, timeout=15
            )
            if response.status_code != 200:
                logging.error(
                    f"REVOLUT: get_balances failed with status {response.status_code}: {response.text}"
                )
                return None
            return response.json()
        except Exception as e:
            logging.critical(e, exc_info=True)
            return None

    def get_gbp_balance(self):
        balances = self.get_balances()
        if not balances:
            return None
        gbp_balances = list(filter(lambda x: x["currency"] == "GBP", balances))
        if not gbp_balances:
            return 0.0
        return float(gbp_balances[0]["available"])

    def place_order(self, symbol="BTC-GBP", side="buy", quote_size="60"):
        if not IS_PROD:
            logging.info(f"REVOLUT: Mocking place_order for {symbol} (Non-PROD)")
            return {
                "data": {
                    "venue_order_id": "mock-venue-order-id",
                    "client_order_id": "mock-client-order-id",
                    "state": "filled",
                }
            }

        method = "POST"
        path = "/api/1.0/orders"
        client_order_id = str(uuid.uuid4())
        timestamp = time.time_ns() // 1_000_000
        payload = json.dumps(
            {
                "client_order_id": client_order_id,
                "symbol": symbol,
                "side": side,
                "order_configuration": {"market": {"quote_size": quote_size}},
            },
            separators=(",", ":"),
        )
        headers = {
            "Accept": "application/json",
            "X-Revx-API-Key": self.api_key,
            "X-Revx-Timestamp": str(timestamp),
            "X-Revx-Signature": self._get_signature(
                timestamp, method, path, "", payload
            ),
        }
        try:
            response = http_client.request(
                method,
                f"{self.base_url}{path}",
                headers=headers,
                data=payload,
                timeout=15,
            )
            if response.status_code not in [200, 201]:
                logging.error(
                    f"REVOLUT: place_order failed with status {response.status_code}: {response.text}"
                )
                return None
            return response.json()
        except Exception as e:
            logging.critical(e, exc_info=True)
            return None
