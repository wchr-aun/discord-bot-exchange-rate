import logging

import requests


class Blockchain:

    def __init__(self) -> None:
        self.EXCHANGE_URL = "https://api.blockchain.info/charts/mvrv?timespan=1year&sampled=true&metadata=false&daysAverageString=1d&cors=true&format=json"

    def call_blockchain_com_chart_api(self) -> dict:
        try:
            response = requests.request("GET", self.EXCHANGE_URL, timeout=15)
            status_code = response.status_code
            if status_code != 200:
                logging.warn("call_blockchain_com_chart_api not getting a 200 response")
                return None
            return response.json()
        except Exception as e:
            logging.critical(e, exc_info=True)
            return None

    def get_mvrv(self) -> int:
        response = self.call_blockchain_com_chart_api()
        if response == None:
            return None
        return (response["values"][-1]["x"], response["values"][-1]["y"])
