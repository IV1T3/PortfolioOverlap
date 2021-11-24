import itertools
import pprint
from tqdm import tqdm

from data.etf_list import ETF_LIST

from main import calculate_overlapping_percentage, get_fund_data

pp = pprint.PrettyPrinter(indent=4)

PORTFOLIO_DATA = {
    "TSLA": 22.46,
    "AAPL": 6.99,
    "BRKB": 6.18,
    "MSFT": 5.78,
    "ILMN": 4.15,
    "MRK": 3.86,
    "AMZN": 3.85,
    "LIN": 3.69,
    "JNJ": 3.53,
    "HD": 3.41,
    "UL": 3.38,
    "PG": 3.32,
    "LMT": 3.07,
    "TXN": 2.76,
    "NVS": 2.75,
    "SYK": 2.46,
    "DIS": 2.23,
    "BMY": 1.92,
    "RHHBY": 1.85,
    "SRT3": 1.66,
    "PLTR": 1.64,
    "WMT": 1.43,
    "NVDA": 1.43,
    "NKE": 1.33,
    "CRM": 1.24,
    "SQ": 1.14,
    "SBUX": 1.14,
    "PACB": 0.63,
    "TWST": 0.57,
}

# ETF_LIST = [
#     {"AAPL": 33.0, "MSFT": 33.0, "AMZN": 33.0},
#     {"AAPL": 50.0, "LMT": 50.0},
#     {
#         "MSFT": 50.0,
#         "SQ": 50.0,
#     },
# ]

all_etfs = []
for etf_isin, v in ETF_LIST.items():
    etf_data = get_fund_data(
        ETF_LIST[etf_isin]["issuer"], ETF_LIST[etf_isin]["url"]
    )
    holdings_dict = {holding[0]: holding[2] for holding in etf_data["holdings"]}
    all_etfs.append(holdings_dict)

etf_powerset = [
    list(x)
    for length in range(1, len(all_etfs) + 1)
    for x in itertools.combinations(all_etfs, length)
]

etf_powerset_combined = []
for etf_combination in etf_powerset:
    all_etf_holdings = {}
    for single_etf in etf_combination:
        for key in single_etf:
            try:
                all_etf_holdings[key] += single_etf[key]
            except KeyError:
                all_etf_holdings[key] = single_etf[key]
    sum_of_holdings = sum([v for _, v in all_etf_holdings.items()])
    for key in all_etf_holdings:
        all_etf_holdings[key] /= sum_of_holdings
    etf_powerset_combined.append(all_etf_holdings)

pp.pprint(etf_powerset_combined)

best_etf_combinations = []
for etf_combination in tqdm(etf_powerset_combined):
    adjusted_etf_combination = {"holdings": []}
    adjusted_etf_combination["holdings"] = [
        [k, "", v]
        for etf_combination in etf_powerset_combined
        for k, v in etf_combination.items()
    ]
    print(adjusted_etf_combination)
    overlapping = calculate_overlapping_percentage(
        adjusted_etf_combination, PORTFOLIO_DATA
    )
    best_etf_combinations.append(overlapping)
pp.pprint(best_etf_combinations)