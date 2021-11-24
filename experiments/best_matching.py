from itertools import combinations, permutations

# TODO:
# Berechne bestes matching mit mehreren ETFs
#   Welche ETFs zusammen bilden Portfolio am besten ab?
#   Alle möglichen Permutationen
#   Overlap percent maximieren
#   Overlap holdings summe equal portfolio weight

def calculate_overlapping_percentage(etf_data, portfolio_data):
    shares_in_common = []
    total_overlap_percentage = 0.0
    overlap_sum = 0.0
    etf_weight_sum = sum(etf_data.values())
    portfolio_weight_sum = sum(portfolio_data.values())
    for etf_position_symbol, etf_position_weight in etf_data.items():
        if etf_position_symbol in portfolio_data:
            shares_in_common.append(etf_position_symbol)
            portfolio_position_weight = portfolio_data[etf_position_symbol]
            overlap_sum += min(etf_position_weight, portfolio_position_weight)
    total_overlap_percentage = (
        2 * (overlap_sum) / (etf_weight_sum + portfolio_weight_sum)
    )

    return shares_in_common, total_overlap_percentage


my_portfolio = {"AAPL": 0.1, "TSLA": 0.5, "MSFT": 0.4}
etf_1 = {"AAPL": 0.1, "TSLA": 0.1, "MSFT": 0.9}
etf_2 = {"TSLA": 0.4, "AMZN": 0.6}

best_matching_percentages = {
    "overall": 0.0,
    "etf_1": 0.0,
    "etf_2": 0.0,
    "AAPL": 0.0,
    "TSLA": 0.0,
}

all_etf_percent_permutations = list(
    filter(lambda x: x[0] + x[1] == 100, list(permutations(range(101), 2)))
)
# print(all_etf_percent_combinations)

for percentage_permuation in all_etf_percent_permutations:
    composed_etf = {}
    percent_etf_1_float = percentage_permuation[0] / 100
    percent_etf_2_float = percentage_permuation[1] / 100
    # percent_aapl = percentage_permuation[2] / 100
    # percent_tsla = percentage_permuation[3] / 100
    # percent_msft = percentage_permuation[4] / 100
    # print(f"{percent_etf_1_float=}")
    # print(f"{percent_etf_2_float=}")
    new_etf_1 = {k: v * percent_etf_1_float for k, v in etf_1.items()}
    new_etf_2 = {k: v * percent_etf_2_float for k, v in etf_2.items()}

    # print(new_etf_1)
    # print(new_etf_2)

    for symbol, percentage in new_etf_1.items():
        if symbol in composed_etf:
            composed_etf[symbol] += percentage * percent_etf_1_float
        else:
            composed_etf[symbol] = percentage * percent_etf_1_float

    for symbol, percentage in new_etf_2.items():
        if symbol in composed_etf:
            composed_etf[symbol] += percentage * percent_etf_2_float
        else:
            composed_etf[symbol] = percentage * percent_etf_2_float

    # if "AAPL" in composed_etf:
    #     composed_etf["AAPL"] += percent_aapl
    # else:
    #     composed_etf["AAPL"] = percent_aapl

    # if "TSLA" in composed_etf:
    #     composed_etf["TSLA"] += percent_tsla
    # else:
    #     composed_etf["TSLA"] = percent_tsla

    # if "MSFT" in composed_etf:
    #     composed_etf["MSFT"] += percentage * percent_msft
    # else:
    #     composed_etf["MSFT"] = percentage * percent_msft

    # print(composed_etf)

    shares_in_common, new_matching_percentage = calculate_overlapping_percentage(
        composed_etf, my_portfolio
    )

    if new_matching_percentage > best_matching_percentages["overall"]:
        print("New best match found:", new_matching_percentage, "% matching!")
        print("ETF1:", percent_etf_1_float, "- ETF2:", percent_etf_2_float)
        best_matching_percentages["overall"] = new_matching_percentage
        best_matching_percentages["etf_1"] = percent_etf_1_float
        best_matching_percentages["etf_2"] = percent_etf_2_float
        # best_matching_percentages["AAPL"] = percent_aapl
        # best_matching_percentages["TSLA"] = percent_tsla
        print("----")

print(best_matching_percentages)