from json import load
import time

import yfinance as yf

from utils.io import load_json_data, write_json_data


class Ticker:
    def __init__(self, ticker, options):
        self.ticker = ticker
        self.options = options
        self.ticker_isin_mapping = load_json_data("ticker_isin_mapping")
        self.isin_company_mapping = load_json_data("isin_company_mapping")

    def to_isin(self):
        if not self.ticker in self.ticker_isin_mapping:
            yf_data = yf.Ticker(self.ticker)
            try:
                if yf_data.isin != "-":
                    self.ticker_isin_mapping[self.ticker] = yf_data.isin
                    self.isin_company_mapping[yf_data.isin] = [
                        yf_data.info["longName"],
                        self.ticker,
                        [self.ticker],
                        # TODO: Is Equity really not an ETF?
                        False,
                        yf_data.info["regularMarketPrice"],
                        time.time(),
                    ]
                else:
                    self.ticker_isin_mapping[self.ticker] = "-"
            except TypeError:
                self.ticker_isin_mapping[self.ticker] = "-"

            self.save()

        return self.ticker_isin_mapping[self.ticker]

    def exists(self):
        return self.ticker in self.ticker_isin_mapping

    def save(self):
        write_json_data(
            "ticker_isin_mapping",
            self.ticker_isin_mapping,
            self.options["io.saveHumanReadable"],
        )
        write_json_data(
            "isin_company_mapping",
            self.isin_company_mapping,
            self.options["io.saveHumanReadable"],
        )
