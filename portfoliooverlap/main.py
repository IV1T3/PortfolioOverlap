import copy
import json
import yaml
import time

from dotenv import load_dotenv

from yaml.loader import SafeLoader

import pprint

from tqdm import tqdm

from apis.alpha_vantage import AlphaVantage

from primitives.holding import Holding
from primitives.etf import ETF
from primitives.isin import ISIN


def load_settings():
    with open("portfoliooverlap/settings.json") as f:
        settings_json = json.load(f)
    return settings_json


def get_shares_in_common(portfolio_a, portfolio_b):
    shares_in_common = []
    for position_a in portfolio_a:
        if position_a in portfolio_b:
            shares_in_common.append(position_a)

    return shares_in_common


def calculate_overlapping_percentage(etf_data, holdings):
    shares_in_common = []
    total_overlap_percentage = 0.0
    individual_overlaps = []
    etf_holdings = etf_data["holdings"]
    etf_weight_sum = sum([position[2] for position in etf_holdings]) / 100
    portfolio_weight_sum = sum(
        [holding.portfolio_percentage for _, holding in holdings.items()]
    )

    for etf_position in etf_holdings:
        etf_position_isin = etf_position[0]
        etf_position_name = etf_position[1]
        etf_position_weight = etf_position[2]
        for holding_isin in holdings:
            if etf_position_isin == holding_isin:
                portfolio_position_weight = holdings[holding_isin].portfolio_percentage
                ind_overlap = min(etf_position_weight / 100, portfolio_position_weight)
                individual_overlaps.append(ind_overlap)
                shares_in_common.append(etf_position_name)
    total_overlap_percentage = (
        2 * (sum(individual_overlaps)) / (etf_weight_sum + portfolio_weight_sum)
    )

    return shares_in_common, total_overlap_percentage


def download_etf_holdings_data(options, etf_list_yaml):

    download_pbar = tqdm(etf_list_yaml, desc="Updating ETF holdings")

    for etf_isin in download_pbar:
        etf_obj = ETF(etf_isin, options)
        if not etf_obj.exists():
            etf_obj.create(
                etf_list_yaml[etf_isin]["issuer"], etf_list_yaml[etf_isin]["url"]
            )


def get_matching_etfs(portfolio_holdings):
    matching_etfs = {}

    etf_holdings_data = load_etf_holdings_data()

    for single_etf_isin in etf_holdings_data:
        single_etf_holdings = etf_holdings_data[single_etf_isin]
        overlapping = calculate_overlapping_percentage(
            single_etf_holdings, portfolio_holdings
        )
        matching_etfs[single_etf_isin] = overlapping

    return matching_etfs


def beautiful_output(matching_etfs, etf_list_yaml):
    sorted_etfs = {
        k: v
        for k, v in sorted(
            matching_etfs.items(), key=lambda item: item[1][1], reverse=True
        )
    }
    no_overlap = []
    print("------")
    print("ETFs sorted by weighted overlap in descending order")
    print("------")
    for etf_isin in sorted_etfs:
        rounded_overlap = round(sorted_etfs[etf_isin][1] * 100, 4)
        amount_top_holdings = (
            5 if len(sorted_etfs[etf_isin][0]) > 5 else len(sorted_etfs[etf_isin][0])
        )
        # TODO: ARK Innovation for example a bit above 100% overlap??
        if rounded_overlap > 100:
            rounded_overlap = 100.0
        if rounded_overlap > 0.0:
            print(etf_list_yaml[etf_isin]["name"])
            print(f"Overlap: {rounded_overlap}%")
            # print("---")
            print(f"Top {amount_top_holdings}: ", end="")
            for i, holding in enumerate(sorted_etfs[etf_isin][0][:amount_top_holdings]):
                print(f"{holding}", end=", " if i < amount_top_holdings - 1 else "\n")
            # print("---")
            # print(
            #     "Other overlapping holdings:",
            #     sorted_etfs[etf_isin][0][amount_top_holdings:],
            # )
            # print("------------")
            print("------------")
        else:
            no_overlap.append(etf_isin)

    if len(no_overlap) > 0:
        print("No overlap found in:")
        for no_overlap_isin in no_overlap:
            print(f"{no_overlap_isin} - {etf_list_yaml[no_overlap_isin]['name']}")


def calculate_holding_percentage(holdings):
    portfolio_sum = 0

    for _, holding in holdings.items():
        portfolio_sum += holding.quantity * holding.price

    for _, holding in holdings.items():
        holding.portfolio_percentage = holding.quantity * holding.price / portfolio_sum

    return holdings


def get_cached_holdings_of_single_etf(isin):
    etf_holdings_data = load_etf_holdings_data()

    if isin in etf_holdings_data:
        return etf_holdings_data[isin]["holdings"]
    else:
        return None


def resolve_etfs_into_individual_holdings(holdings):

    resolved_holdings = copy.deepcopy(holdings)

    resolving_pbar = tqdm(holdings, desc="Resolving ETFs")

    for holding_isin in resolving_pbar:
        if holdings[holding_isin].is_etf:
            # print(f"{holdings[holding_isin].name} is an ETF. Resolving...")
            # if get_quote_type(holdings[holding_isin].main_ticker) == "ETF":
            single_etf_holdings = get_cached_holdings_of_single_etf(holding_isin)

            # print(f"{single_etf_holdings=}")

            if single_etf_holdings is None:
                print(
                    f"{holdings[holding_isin].name} is currently not supported. Aborting Resolution."
                )
            else:
                for single_etf_position in single_etf_holdings:
                    single_etf_position_isin = single_etf_position[0]
                    single_etf_position_name = single_etf_position[1]
                    single_etf_position_percentage = single_etf_position[2]

                    etf_position_appending_percentage = (
                        holdings[holding_isin].portfolio_percentage
                        * single_etf_position_percentage
                        / 100
                    )

                    if single_etf_position_isin in holdings:
                        resolved_holdings[
                            single_etf_position_isin
                        ].portfolio_percentage += etf_position_appending_percentage

                        # TODO: Calc correct quantity
                        # holdings[single_etf_position_isin].quantity += 0
                    else:
                        # print(f"Adding {single_etf_position_name} to holdings...")
                        # print(f"{single_etf_position_name} quantity: ??")
                        # print(f"{single_etf_position_name} price: ??")

                        isin_obj = ISIN(single_etf_position_isin)
                        resolved_holdings[single_etf_position_isin] = Holding(
                            name=single_etf_position_name,
                            isin=single_etf_position_isin,
                            main_ticker=isin_obj.to_ticker(),
                            tickers=isin_obj.to_ticker(all_tickers=True),
                            # TODO: Calc correct quantity and fetch price
                            quantity=0.0,
                            price=0.0,
                            # TODO: ETF might contain another ETF!
                            is_etf=False,
                            portfolio_percentage=etf_position_appending_percentage,
                        )

                resolved_holdings[holding_isin].quantity = 0.0
                resolved_holdings[holding_isin].portfolio_percentage = 0.0
                resolved_holdings[holding_isin].etf_resolved = True

    return resolved_holdings


def load_portfolio():
    with open("portfolio.yml") as f:
        portfolio_data_yaml = yaml.load(f, Loader=SafeLoader)
    return portfolio_data_yaml


def load_etf_list():
    with open("portfoliooverlap/data/etf_list.yml") as f:
        etf_list_yaml = yaml.load(f, Loader=SafeLoader)
    return etf_list_yaml


def load_etf_holdings_data():
    try:
        with open("portfoliooverlap/data/etf_holdings_data.json", "r") as f:
            etf_data = json.load(f)
    except json.decoder.JSONDecodeError:
        etf_data = {}
    except FileNotFoundError:
        etf_data = {}

    return etf_data


if __name__ == "__main__":
    pp = pprint.PrettyPrinter(indent=4)
    current_time = time.time()
    load_dotenv()

    portfolio_holdings = {}
    collecting_tickers_successful = True

    options = load_settings()
    portfolio_data_yaml = load_portfolio()
    etf_list_yaml = load_etf_list()

    portfolio_isin_pbar = tqdm(portfolio_data_yaml, desc="Collecting stock information")

    # Fetching tickers
    for i, isin in enumerate(portfolio_isin_pbar):
        isin_obj = ISIN(isin)
        if not isin_obj.exists():
            isin_obj.create()

    # Preparing portfolio holdings
    holdings_pbar = tqdm(portfolio_data_yaml, desc="Preparing holdings")
    for i, isin in enumerate(holdings_pbar):
        isin_obj = ISIN(isin)
        holding = Holding(
            name=isin_obj.get_name(),
            isin=isin,
            main_ticker=isin_obj.to_ticker(),
            tickers=isin_obj.to_ticker(all_tickers=True),
            quantity=portfolio_data_yaml[isin],
            price=isin_obj.get_quote(),
            is_etf=isin_obj.is_etf(),
        )
        portfolio_holdings[isin] = holding

    if collecting_tickers_successful:
        download_etf_holdings_data(options, etf_list_yaml)

        portfolio_holdings = calculate_holding_percentage(portfolio_holdings)
        portfolio_holdings = resolve_etfs_into_individual_holdings(portfolio_holdings)

        matching_etfs = get_matching_etfs(portfolio_holdings)
        beautiful_output(matching_etfs, etf_list_yaml)
