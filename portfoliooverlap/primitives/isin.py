import time

import investpy

from apis.alpha_vantage import AlphaVantage
from apis.open_figi import OpenFigi

from utils.io import load_json_data, write_json_data
from utils.utils import get_quote_type


class ISIN:
    def __init__(self, isin):
        self.isin = isin
        self.isin_price_mapping = load_json_data("isin_price_mapping")
        self.isin_ticker_mapping = load_json_data("isin_ticker_mapping")
        self.ticker_isin_mapping = load_json_data("ticker_isin_mapping")

        if isin in self.isin_ticker_mapping:
            self.holding_is_etf = self.isin_ticker_mapping[isin][3]
        else:
            self.holding_is_etf = False

        self.open_figi = OpenFigi()
        self.alpha_vantage = AlphaVantage()

    def create(self):
        # InvestPy Approach
        company_name, tickers, main_ticker = "", [], ""
        investpy_success = False

        try:
            data = investpy.stocks.search_stocks("isin", self.isin).to_dict()
            investpy_success = True
        except RuntimeError:
            try:
                data = investpy.etfs.search_etfs("isin", self.isin).to_dict()
                investpy_success = True
                self.holding_is_etf = True
            except RuntimeError:
                pass

        if not investpy_success:
            # OpenFigi Approach
            company_name, tickers, main_ticker = self.open_figi.get_tickers_by_isin(
                self.isin
            )
            if "ETF" == get_quote_type(main_ticker):
                self.holding_is_etf = True
        else:
            company_name = data["full_name"][0]
            tickers = list(data["symbol"].values())
            main_ticker = tickers[0]

        tickers = list(set(tickers))

        self.isin_ticker_mapping[self.isin] = [
            company_name,
            main_ticker,
            tickers,
            self.holding_is_etf,
            time.time(),
        ]

        print(f"{self.isin_ticker_mapping[self.isin]=}")

        quote = float(self.alpha_vantage.get_quote_by_symbol(main_ticker))
        self.isin_price_mapping[self.isin] = quote

        for ticker in tickers:
            self.ticker_isin_mapping[ticker] = self.isin

        self.save()

    def exists(self):
        return self.isin in self.isin_ticker_mapping

    def to_ticker(self, all_tickers=False):
        if not self.exists():
            self.create()

        if all_tickers:
            return self.isin_ticker_mapping[self.isin][2]
        else:
            return self.isin_ticker_mapping[self.isin][1]

    def get_quote(self):
        if not self.isin in self.isin_price_mapping:
            self.create()

        if self.isin in self.isin_price_mapping:
            return self.isin_price_mapping[self.isin]
        else:
            return None

    def get_name(self):
        return self.isin_ticker_mapping[self.isin][0]

    def is_etf(self):
        return self.holding_is_etf

    def save(self):
        write_json_data("isin_ticker_mapping", self.isin_ticker_mapping)
        write_json_data("isin_price_mapping", self.isin_price_mapping)
        write_json_data("ticker_isin_mapping", self.ticker_isin_mapping)
