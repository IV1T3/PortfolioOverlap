import requests
from time import sleep


class OpenFigi:

    _OPEN_FIGI_API_URL = "https://api.openfigi.com/v3/"
    _OPEN_FIGI_HEADERS = {"Content-Type": "application/json"}

    def __init__(self):
        pass

    def _perform_api_request(self, api_type, id_type, id_value):

        payload = '[{"idType":"' + id_type + '","idValue":"' + id_value + '"}]'
        response = requests.post(
            self._OPEN_FIGI_API_URL + api_type,
            headers=self._OPEN_FIGI_HEADERS,
            data=payload,
        )
        data = response.json()[0]["data"]
        sleep(12)
        return data

    def get_tickers_by_isin(self, isin):
        data = self._perform_api_request("mapping", "ID_ISIN", isin)

        tickers = []
        company_name = data[0]["name"]
        main_ticker = ""

        for i in range(len(data)):
            ticker = data[i]["ticker"]
            if "/" in ticker:
                ticker = ticker.replace("/", ".")

            if data[i]["exchCode"] == "US":
                main_ticker = ticker
            tickers.append(ticker)

        return company_name, list(set(tickers)), main_ticker
