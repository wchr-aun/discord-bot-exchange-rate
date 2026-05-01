import pytest
from unittest.mock import MagicMock, patch
from external.ApiLayer import ExchangeAPI
from external.Binance import BinanceApi
from external.Blockchain import Blockchain


def test_apilayer_get_rate_success():
    api = ExchangeAPI("dummy_key")
    with patch("requests.request") as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {"rates": {"THB": 45.0}}

        # Force IS_PROD to True for this test to actually call the mock
        with patch("external.ApiLayer.IS_PROD", True):
            rate = api.get_rate("GBP", "THB")
            assert rate == 45.0


def test_binance_get_btc_price_success():
    api = BinanceApi()
    with patch("requests.request") as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {"price": "60000.0"}

        price = api.get_btc_price()
        assert price == "60000.0"


def test_blockchain_get_mvrv_success():
    api = Blockchain()
    with patch("requests.request") as mock_get:
        with patch("external.Blockchain.IS_PROD", True):
            mock_get.return_value.status_code = 200
            mock_get.return_value.json.return_value = {
                "values": [{"x": 1600000000, "y": 2.5}]
            }

            timestamp, mvrv = api.get_mvrv()
            assert timestamp == 1600000000
            assert mvrv == 2.5
