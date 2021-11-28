import os
import requests
from time import sleep


class AlphaVantage:

    _ALPHA_VANTAGE_API_URL = "https://www.alphavantage.co/query?"

    def __init__(self, api_key=None):

        if api_key is None:
            api_key = os.getenv("ALPHA_VANTAGE_API_KEY")

        if not api_key or not isinstance(api_key, str):
            raise ValueError(
                "No API key provided. (ALPHA_VANTAGE_API_KEY environment variable)"
            )

        self.api_key = api_key

    def _perform_api_request(self, url):
        print(f"{url=}")
        response = requests.get(url)
        data = response.json()
        sleep(12)
        return data

    def get_company_by_keyword(self, keyword):
        url = (
            self._ALPHA_VANTAGE_API_URL
            + "function=SYMBOL_SEARCH&keywords="
            + keyword
            + "&apikey="
            + self.api_key
        )
        return self._perform_api_request(url)

    def get_quote_by_symbol(self, symbol):
        url = (
            self._ALPHA_VANTAGE_API_URL
            + "function=GLOBAL_QUOTE&symbol="
            + symbol
            + "&apikey="
            + self.api_key
        )
        data = self._perform_api_request(url)
        quote = data["Global Quote"]["05. price"]
        return quote
