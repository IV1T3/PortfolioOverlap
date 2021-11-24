import time
import cloudscraper
import requests
import csv
import pyexcel as pe

from apis.alpha_vantage import AlphaVantage

from primitives.isin import ISIN
from primitives.ticker import Ticker

from utils.io import load_json_data, write_json_data
from utils.utils import format_date


class ETF:
    def __init__(self, isin, options=None):
        self.isin = isin
        self.options = options
        self.alpha_vantage = AlphaVantage()
        self.isin_ticker_mapping = load_json_data("isin_ticker_mapping")
        self.ticker_isin_mapping = load_json_data("ticker_isin_mapping")
        self.isin_price_mapping = load_json_data("isin_price_mapping")
        self.all_cached_etf_holdings = load_json_data("etf_holdings_data")

    def _download_etf_holdings(self, issuer, parse_url):
        if issuer == "ARK":
            scraper = cloudscraper.create_scraper()
            raw_holdings = scraper.get(parse_url).content
        elif issuer == "iShares":
            response = requests.get(parse_url)
            raw_holdings = list(csv.reader(response.text.strip().split("\n")))
        elif issuer == "Lyxor":
            response = requests.get(parse_url)
            raw_holdings = response.content

        return raw_holdings

    def _parse_raw_holdings(self, raw_holdings, issuer):

        etf_data = {"holdings": [], "updated": time.time()}

        idcs = {
            "ARK": {"ticker": 3, "name": 2, "weight": 5},
            "iShares": {"ticker": 0, "name": 1, "weight": 5, "description": 2},
            "Lyxor": {"ticker": 2, "name": 4, "weight": 5},
        }

        if issuer == "ARK":
            text_splits = raw_holdings.decode().split("\n")
            description = text_splits[:1]
            holdings = text_splits[1:]

            for i, holding in enumerate(holdings):
                holding = holding.split(',(?=(?:[^"]*"[^"]*")*[^"]*$)')[0].split(",")
                if len(holding) > 1:
                    holding = [
                        holding[0],
                        holding[1],
                        holding[2][1:-1],
                        holding[3],
                        holding[4],
                        holding[-1],
                    ]

                    holdings[i] = holding

            holdings = holdings[:-2]

            parsed_date = format_date(holdings[0][0])

        elif issuer == "iShares":
            # description = raw_holdings[idcs[issuer]["description"]]
            # idcs[issuer]["weight"] = 3 if description[3] == "Gewichtung (%)" else 4

            holdings = raw_holdings[3:]
            parsed_date = format_date(raw_holdings[0][1])

        elif issuer == "Lyxor":
            key = "Holdings & Exposure Constituant"

            holdings = pe.get_book_dict(file_type="xls", file_content=raw_holdings)[
                key
            ][7:][7:]
            parsed_date = format_date(holdings[0][0].split(":")[1])

        etf_data["updated"] = parsed_date

        for holding in holdings:
            raw_weight = holding[idcs[issuer]["weight"]]

            if issuer == "ARK":
                weight = float(raw_weight[:-1])
            else:
                weight = float(raw_weight.replace(".", "").replace(",", "."))

            if weight > self.options["etf.minPercentage"]:
                print(f"{holding=}")

                name = holding[idcs[issuer]["name"]]
                holding_ticker = holding[idcs[issuer]["ticker"]]

                name = " ".join(
                    list(filter(lambda word: len(word) > 1, name.split(" ")))
                )
                name = " ".join(
                    list(filter(lambda word: "-" not in word, name.split(" ")))
                )
                longest_words = sorted(name.split(" "), key=len, reverse=True)
                # print(longest_words)

                best_matches_not_found = True

                av_result = self.alpha_vantage.get_company_by_keyword(holding_ticker)
                if "bestMatches" in av_result:
                    best_matches = av_result["bestMatches"]

                    if len(best_matches) > 0:
                        best_matches_not_found = False

                if best_matches_not_found:
                    av_result = self.alpha_vantage.get_company_by_keyword(name)
                    if "bestMatches" in av_result:
                        best_matches = av_result["bestMatches"]

                        if len(best_matches) > 0:
                            best_matches_not_found = False

                if not best_matches_not_found:
                    # print(best_matches)

                    collected_tickers = []
                    for match in best_matches:
                        if float(match["9. matchScore"]) > 0.4:
                            if longest_words[0].lower() in match["2. name"].lower():
                                if (
                                    len(longest_words) > 1
                                    and longest_words[1].lower()
                                    in match["2. name"].lower()
                                ):
                                    collected_tickers.append(
                                        [
                                            match["1. symbol"],
                                            float(match["9. matchScore"]),
                                        ]
                                    )
                                else:
                                    collected_tickers.append(
                                        [
                                            match["1. symbol"],
                                            float(match["9. matchScore"]),
                                        ]
                                    )
                    # print(f"{collected_tickers=}")

                    ticker_weighting = {}
                    for ticker in collected_tickers:
                        if ticker[0] in ticker_weighting:
                            ticker_weighting[ticker[0]] += ticker[1]
                        else:
                            ticker_weighting[ticker[0]] = ticker[1]

                    ticker_weighting = list(
                        filter(
                            lambda ticker: "." not in ticker[0],
                            ticker_weighting.items(),
                        )
                    )
                    ticker_weighting = sorted(
                        ticker_weighting, key=lambda ticker: ticker[1], reverse=True
                    )

                    print(f"{ticker_weighting=}")

                    main_ticker = ticker_weighting[0][0]

                    print(f"{main_ticker=}")

                    ticker_obj = Ticker(main_ticker)
                    holding_isin = ticker_obj.to_isin()

                    # TODO: Improve handling of ISIN not found
                    if holding_isin != "-":
                        etf_data["holdings"].append([holding_isin, name, weight])

                        isin_obj = ISIN(holding_isin)
                        if not isin_obj.exists():
                            isin_obj.create()

        return etf_data

    def exists(self):
        return self.isin in self.all_cached_etf_holdings

    def create(self, issuer, parse_url):
        raw_holdings = self._download_etf_holdings(issuer, parse_url)

        etf_holdings = self._parse_raw_holdings(raw_holdings, issuer)

        self.all_cached_etf_holdings[self.isin] = etf_holdings

        write_json_data(
            "etf_holdings_data",
            self.all_cached_etf_holdings,
            self.options["io.saveHumanReadable"],
        )

        return etf_holdings
