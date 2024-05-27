import logging

import requests


class FaithInOpenrent:

    def __init__(self) -> None:
        self.FOR_URL = "https://faith-in-openrent.vercel.app/search/all"

    def get_for(self) -> dict:
        try:
            response = requests.request("GET", self.FOR_URL, timeout=15)
            status_code = response.status_code
            if status_code != 200:
                logging.warn("call_blockchain_com_chart_api not getting a 200 response")
                return None
            return response.json()
        except Exception as e:
            logging.critical(e, exc_info=True)
            return None
