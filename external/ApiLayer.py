import logging

import requests

from setup import IS_PROD


class ExchangeAPI:

    def __init__(self, exchange_api: str) -> None:
        self.EXCHANGE_API = exchange_api
        self.EXCHANGE_URL = (
            "https://api.apilayer.com/exchangerates_data/latest?symbols=THB&base=GBP"
        )

    def get_gbp_to_thb(self) -> dict:
        payload = {}
        headers = {"apikey": self.EXCHANGE_API}

        try:
            response = requests.request(
                "GET", self.EXCHANGE_URL, headers=headers, data=payload, timeout=15
            )

            status_code = response.status_code
            if status_code != 200:
                logging.warn("EXCHANGE: get_gbp_to_thb not getting a 200 response")
                return None
            return response.json()
        except Exception as e:
            logging.critical(e, exc_info=True)
            return None

    def get_rates_thb(self) -> float:
        rates = self.get_gbp_to_thb() if IS_PROD else {"rates": {"THB": 45}}
        if rates is None:
            return None
        return rates["rates"]["THB"]
