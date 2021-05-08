import copy
import cloudscraper
import csv
import dateparser
import io
import PyPDF2
import requests

from tqdm import tqdm

from etf_data import ETF_DATA_TEMPLATE, ETF_DATA_EXAMPLE
from etf_list import ETF_LIST
from portfolio import PORTFOLIO_DATA

# TODO:
# Rekursive ETF Aufloesung in Portfolio

# USAGE
# 1. Customize file portfolio.py to fit your portfolio
# 2. pip3 install -r requirements.txt
# 3. python3 etf_overlap.py


def chunks(lst, n):
    # https://stackoverflow.com/questions/312443/how-do-you-split-a-list-into-evenly-sized-chunks
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i : i + n]


def format_data(date):
    return dateparser.parse(date).strftime("%d.%m.%Y")


def parse_ark_pdf(pdf_content):
    # Read data from Bytes Buffer
    pdf_bytes_buffer = io.BytesIO(pdf_content)
    pdf_reader = PyPDF2.PdfFileReader(pdf_bytes_buffer)
    pdf_number_pages = pdf_reader.getNumPages()
    pdf_text = ""
    for i in range(pdf_number_pages):
        pdf_text += pdf_reader.getPage(i).extractText()

    text_splits = pdf_text.split("\n")
    description = text_splits[:8]
    ark_holdings = list(chunks(text_splits[8:], 7))

    # Parse data into ETF structure
    parsed_date = format_data(description[1].split(" ")[2])

    # Fill ETF_DATA
    etf_data = copy.deepcopy(ETF_DATA_TEMPLATE)
    etf_data["date"] = parsed_date
    ticker_index = 2
    name_index = 1
    weight_index = 6

    for position in ark_holdings:
        if position[0].isdigit() and position[3].isdigit():
            symbol = position[ticker_index]
            name = position[name_index]
            weight = float(position[weight_index])
            etf_data["holdings"].append([symbol, name, weight])

    return etf_data


def parse_ishares_csv(wrapper):
    etf_data = copy.deepcopy(ETF_DATA_TEMPLATE)
    parsed_date = format_data(wrapper[0][1])
    etf_data["date"] = parsed_date
    description = wrapper[2]
    ticker_index = 0
    name_index = 1
    weight_index = 3 if description[3] == "Gewichtung (%)" else 4
    for position in wrapper[3:]:
        weight = float(position[weight_index].replace(".", "").replace(",", "."))
        if weight > 0.0:
            symbol = position[ticker_index]
            name = position[name_index]
            etf_data["holdings"].append([symbol, name, weight])

    return etf_data


def get_shares_in_common(portfolio_a, portfolio_b):
    shares_in_common = []
    for position_a in portfolio_a:
        if position_a in portfolio_b:
            shares_in_common.append(position_a)

    return shares_in_common


def calculate_overlapping_percentage(etf_data, portfolio_data):
    shares_in_common = []
    total_overlap_percentage = 0.0
    overlap_sum = 0.0
    etf_holdings = etf_data["holdings"]
    etf_weight_sum = sum([position[2] for position in etf_holdings])
    portfolio_weight_sum = sum(portfolio_data.values())
    for etf_position in etf_holdings:
        etf_position_symbol = etf_position[0]
        etf_position_weight = etf_position[2]
        if etf_position_symbol in portfolio_data:
            shares_in_common.append(etf_position_symbol)
            portfolio_position_weight = portfolio_data[etf_position_symbol]
            overlap_sum += min(etf_position_weight, portfolio_position_weight)
    total_overlap_percentage = (
        2 * (overlap_sum) / (etf_weight_sum + portfolio_weight_sum)
    )

    return shares_in_common, total_overlap_percentage


def get_ishares_fund_data(url):
    response = requests.get(url)
    wrapper = list(csv.reader(response.text.strip().split("\n")))

    return parse_ishares_csv(wrapper)


def get_ark_fund_data(url):
    scraper = cloudscraper.create_scraper()
    pdf_content = scraper.get(url).content

    return parse_ark_pdf(pdf_content)


def get_fund_data(provider, url):
    if provider == "iShares":
        fund_data = get_ishares_fund_data(url)
    elif provider == "ARK":
        fund_data = get_ark_fund_data(url)

    return fund_data


def get_matching_etfs(portfolio_data):
    matching_etfs = {}
    for etf_ticker in tqdm(ETF_LIST):
        etf_data = get_fund_data(
            ETF_LIST[etf_ticker]["provider"], ETF_LIST[etf_ticker]["url"]
        )
        overlapping = calculate_overlapping_percentage(etf_data, portfolio_data)
        matching_etfs[etf_ticker] = overlapping

    return matching_etfs


def beautiful_output(matching_etfs):
    sorted_etfs = {
        k: v
        for k, v in sorted(
            matching_etfs.items(), key=lambda item: item[1][1], reverse=True
        )
    }
    no_overlap = []
    print("----")
    print("ETFs sorted by weighted overlap in descending order")
    print("----")
    for etf_ticker in sorted_etfs:
        rounded_overlap = round(sorted_etfs[etf_ticker][1] * 100, 4)
        if rounded_overlap > 0.0:
            print(ETF_LIST[etf_ticker]["name"])
            print(f"Overlap: {rounded_overlap}%")
            print("Holdings:", sorted_etfs[etf_ticker][0])
            print("----")
        else:
            no_overlap.append(etf_ticker)
    print("No overlap found in:")
    for no_overlap_ticker in no_overlap:
        print(f"{no_overlap_ticker} - {ETF_LIST[no_overlap_ticker]['name']}")


matching_etfs = get_matching_etfs(PORTFOLIO_DATA)
beautiful_output(matching_etfs)