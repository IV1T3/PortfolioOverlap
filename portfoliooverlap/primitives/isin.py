import time

from apis.alpha_vantage import AlphaVantage
from apis.open_figi import OpenFigi

from apis.interface import Interface

from utils.io import load_json_data, write_json_data


class ISIN:
    def __init__(self, isin, options):
        self.isin = isin
        self.options = options
        self.ticker_isin_mapping = load_json_data("ticker_isin_mapping")
        self.isin_company_mapping = load_json_data("isin_company_mapping")

        if isin in self.isin_company_mapping:
            self.holding_is_etf = self.isin_company_mapping[isin][3]
        else:
            self.holding_is_etf = False

        self.open_figi = OpenFigi()
        self.alpha_vantage = AlphaVantage()
        self.api_interface = Interface()

    def create(self):
        data = self.api_interface.get_data_by_isin(self.isin)

        print(f"{data=}")

        self.isin_company_mapping[self.isin] = [
            data[0],
            data[1],
            data[2],
            data[4] == "ETF",
            data[3],
            time.time(),
        ]

        print(f"{self.isin_company_mapping[self.isin]=}")

        for ticker in data[2]:
            self.ticker_isin_mapping[ticker] = self.isin

        self.save()

    def exists(self):
        return self.isin in self.isin_company_mapping

    def to_ticker(self, all_tickers=False):
        if not self.exists():
            self.create()

        if all_tickers:
            return self.isin_company_mapping[self.isin][2]
        else:
            return self.isin_company_mapping[self.isin][1]

    def get_quote(self):
        if not self.isin in self.isin_company_mapping:
            self.create()

        if self.isin in self.isin_company_mapping:
            return self.isin_company_mapping[self.isin][4]
        else:
            return None

    def get_name(self):
        return self.isin_company_mapping[self.isin][0]

    def is_etf(self):
        return self.holding_is_etf

    def save(self):
        write_json_data(
            "isin_company_mapping",
            self.isin_company_mapping,
            self.options["io.saveHumanReadable"],
        )
        write_json_data(
            "ticker_isin_mapping",
            self.ticker_isin_mapping,
            self.options["io.saveHumanReadable"],
        )
