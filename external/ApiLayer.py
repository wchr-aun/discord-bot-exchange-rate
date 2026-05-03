import logging

from external import http_client
from setup import IS_PROD


class ExchangeAPI:

    def __init__(self, exchange_api: str) -> None:
        self.EXCHANGE_API = exchange_api
        self.BASE_URL = "https://api.apilayer.com/exchangerates_data/latest"

    def get_rates(self, base: str = "GBP", symbols: str = "THB") -> dict:
        payload = {}
        headers = {"apikey": self.EXCHANGE_API}
        url = f"{self.BASE_URL}?symbols={symbols}&base={base}"

        try:
            response = http_client.request(
                "GET", url, headers=headers, data=payload, timeout=15
            )

            status_code = response.status_code
            if status_code != 200:
                logging.warning(
                    f"EXCHANGE: get_rates ({base}-{symbols}) not getting a 200 response"
                )
                return None
            return response.json()
        except Exception as e:
            logging.critical(e, exc_info=True)
            return None

    def get_rate(self, base: str = "GBP", symbol: str = "THB") -> float:
        if not IS_PROD:
            # Mock rates for development
            return 45.0

        rates = self.get_rates(base=base, symbols=symbol)
        if rates is None or "rates" not in rates or symbol not in rates["rates"]:
            return None
        return rates["rates"][symbol]
