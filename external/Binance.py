import logging
import requests


class BinanceApi:

    def __init__(self) -> None:
        self.AVG_PRICE_URL = "https://api.binance.com/api/v3/avgPrice"

    def call_average_price_by_symbol(self, symbol: str) -> dict:
        try:
            response = requests.request(
                "GET", f"{self.AVG_PRICE_URL}?symbol={symbol}", timeout=15
            )
            status_code = response.status_code
            if status_code != 200:
                logging.warn(
                    "BINANCE: call_average_price_by_symbol not getting a 200 response"
                )
                return None
            return response.json()
        except Exception as e:
            logging.critical(e, exc_info=True)
            return None

    def get_btc_price(self):
        response = self.call_average_price_by_symbol("BTCUSDC")
        if response == None:
            return None
        if "price" not in response:
            logging.warning("BINANCE: get_btc_price not having price field")
            return None
        return response["price"]
