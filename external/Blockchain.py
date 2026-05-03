import logging
from datetime import datetime
from external import http_client
from setup import IS_PROD


class Blockchain:

    def __init__(self) -> None:
        self.EXCHANGE_URL = "https://api.blockchain.info/charts/mvrv?timespan=1year&sampled=true&metadata=false&daysAverageString=1d&cors=true&format=json"

    def call_blockchain_com_chart_api(self) -> dict:
        try:
            response = http_client.request("GET", self.EXCHANGE_URL, timeout=15)
            status_code = response.status_code
            if status_code != 200:
                logging.warning(
                    "MVRV: call_blockchain_com_chart_api not getting a 200 response"
                )
                return None
            return response.json()
        except Exception as e:
            logging.critical(e, exc_info=True)
            return None

    def get_mvrv(self) -> tuple:
        if not IS_PROD:
            return (int(datetime.now().timestamp()), 1.5)

        response = self.call_blockchain_com_chart_api()
        if response == None:
            return None
        if (
            "values" not in response
            or not isinstance(response["values"], list)
            or len(response["values"]) == 0
        ):
            logging.warning("MVRV: blockchain_com_chart_api not having values field")
            return None
        last_item = response["values"][-1]
        if "x" not in last_item or "y" not in last_item:
            logging.warning("MVRV: blockchain_com_chart_api not having the last field")
            return None
        return (last_item["x"], last_item["y"])
