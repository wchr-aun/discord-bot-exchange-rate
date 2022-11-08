import os
import requests

class ExchangeAPI:

    def __init__(self, exchange_api: str) -> None:
        self.EXCHANGE_API = exchange_api
        self.EXCHANGE_URL = 'https://api.apilayer.com/exchangerates_data/latest?symbols=THB&base=GBP'

    def get_gbp_to_thb(self) -> dict:
      payload = {}
      headers= {
        "apikey": self.EXCHANGE_API
      }

      response = requests.request("GET", self.EXCHANGE_URL, headers=headers, data = payload)

      status_code = response.status_code
      if status_code != 200:
        return None
      return response.json()

    def get_rates_thb(self) -> float:
      rates = self.get_gbp_to_thb()
      if rates is None:
        return None
      return rates['rates']['THB']