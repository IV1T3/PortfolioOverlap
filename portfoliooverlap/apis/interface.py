import investpy

from apis.alpha_vantage import AlphaVantage
from apis.open_figi import OpenFigi

# ISIN -> investpy/OpenFigi
# Full stock name -> self.alpha_vantage
# Tickers


class Interface:
    def __init__(self) -> None:
        self.alpha_vantage = AlphaVantage()
        self.open_figi = OpenFigi()

    def get_data_by_isin(self, isin, requested_data=None) -> list:
        print("Getting data by ISIN")

        data = []

        if requested_data is None:
            requested_data = ["name", "main_ticker", "tickers", "equity_type", "quote"]

        investpy_full_name = self._get_name_by_isin(isin)

        if "name" in requested_data:
            data.append(investpy_full_name)

        if any(
            data_point in ["main_ticker", "tickers", "quote", "equity_type"]
            for data_point in requested_data
        ):
            av_data = self._get_av_data_by_name(investpy_full_name, requested_data)
            if "main_ticker" in requested_data:
                data.append(av_data["main_ticker"])
            if "tickers" in requested_data:
                data.append(av_data["tickers"])
            if "quote" in requested_data:
                data.append(av_data["quote"])
            if "equity_type" in requested_data:
                data.append(av_data["equity_type"])

        return data

    def _get_name_by_isin(self, isin) -> str:
        print("Getting name by ISIN:", isin)
        investpy_success = True

        try:
            result = investpy.stocks.search_stocks("isin", isin).to_dict()
        except RuntimeError:
            try:
                result = investpy.etfs.search_etfs("isin", isin).to_dict()
            except RuntimeError as e:
                investpy_success = False
                print("Investpy failed:", e)
                pass

        if investpy_success:
            full_equity_name = result["full_name"][0]
        else:
            full_equity_name, _, _ = self.open_figi.get_tickers_by_isin(isin)

        return full_equity_name

    def _get_av_data_by_name(self, name, requested_data=None) -> dict:
        print("Getting AV data by name:", name)
        av_data = {}

        collected_tickers = {}

        name = " ".join(list(filter(lambda word: len(word) > 1, name.split(" "))))
        name = " ".join(list(filter(lambda word: "-" not in word, name.split(" "))))
        name = " ".join(list(filter(lambda word: "SA" not in word, name.split(" "))))

        longest_words = sorted(name.split(" "), key=len, reverse=True)
        best_matches = self.alpha_vantage.get_company_by_keyword(name)["bestMatches"]

        for match in best_matches:
            if float(match["9. matchScore"]) > 0.4:
                if longest_words[0].lower() in match["2. name"].lower():
                    # if (
                    #     len(longest_words) > 1
                    #     and longest_words[1].lower() in match["2. name"].lower()
                    # ):
                    #     collected_tickers[match["1. symbol"]] = [
                    #         float(match["9. matchScore"]),
                    #         match["3. type"],
                    #     ]

                    # else:
                    collected_tickers[match["1. symbol"]] = [
                        float(match["9. matchScore"]),
                        match["3. type"],
                    ]

        collected_tickers = list(
            filter(
                lambda ticker: "." not in ticker[0],
                collected_tickers.items(),
            )
        )
        collected_tickers = sorted(
            collected_tickers, key=lambda ticker: ticker[1][0], reverse=True
        )

        main_ticker = collected_tickers[0][0]

        av_data["main_ticker"] = main_ticker
        av_data["tickers"] = list(
            set([ticker_tuple[0] for ticker_tuple in collected_tickers])
        )

        if "quote" in requested_data:
            av_data["quote"] = float(
                self.alpha_vantage.get_quote_by_symbol(main_ticker)
            )

        if "equity_type" in requested_data:
            equity_type = "STOCK" if collected_tickers[0][1][1] == "Equity" else "ETF"
            av_data["equity_type"] = equity_type

        return av_data
