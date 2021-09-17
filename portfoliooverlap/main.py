import copy
import cloudscraper
import csv
import dateparser
import io
import PyPDF2
import requests
import json
import yaml
import os

from yaml.loader import SafeLoader

import pprint

import pyexcel as pe

from tqdm import tqdm
from time import sleep
from dotenv import load_dotenv

from data.etf_data import ETF_DATA_TEMPLATE
from data.etf_list import ETF_LIST
from holding import Holding

# TODO:
# Rekursive ETF Aufloesung in Portfolio
# Berechne bestes matching mit mehreren ETFs
#   Welche ETFs zusammen bilden Portfolio am besten ab?
#   Alle möglichen Permutationen
#   Overlap percent maximieren
#   Overlap holdings summe equal portfolio weight


def chunks(lst, n):
    return [lst[i:i + n] for i in range(0, len(lst), n)]

def check_float(potential_float):
    try:
        float(potential_float)
        return True
    except ValueError:
        return False


def format_date(date):
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
    ark_holdings = chunks(text_splits[8:], 7)

    # Parse date into ETF structure
    parsed_date = format_date(description[1].split(" ")[2])

    # Fill ETF_DATA
    etf_data = copy.deepcopy(ETF_DATA_TEMPLATE)
    etf_data["date"] = parsed_date
    ticker_index = 2
    name_index = 1
    weight_index = 6

    for position in ark_holdings:
        if position[0].isdigit() and check_float(position[6]):
            symbol = position[ticker_index]
            name = position[name_index]
            weight = float(position[weight_index])
            etf_data["holdings"].append([symbol, name, weight])

    return etf_data


def parse_lyxor_xls(r_content):
    # Read data from XLS Bytes Buffer
    key = "Holdings & Exposure Constituant"
    book = pe.get_book_dict(file_type="xls", file_content=r_content)[key][7:]

    # Parse date into ETF structure
    parsed_date = format_date(book[0][0].split(":")[1])

    # Fill ETF_DATA
    etf_data = copy.deepcopy(ETF_DATA_TEMPLATE)
    etf_data["date"] = parsed_date

    ticker_index = 2
    name_index = 4
    weight_index = 5
    lyxor_holdings = book[7:]
    for position in lyxor_holdings:
        symbol = position[ticker_index]
        name = position[name_index]
        weight = position[weight_index]
        etf_data["holdings"].append([symbol, name, weight])
    return etf_data


def parse_ishares_csv(wrapper):
    etf_data = copy.deepcopy(ETF_DATA_TEMPLATE)
    parsed_date = format_date(wrapper[0][1])
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


def calculate_overlapping_percentage(etf_data, holdings):
    shares_in_common = []
    total_overlap_percentage = 0.0
    # overlap_sum = 0.0
    individual_overlaps = []
    etf_holdings = etf_data["holdings"]
    etf_weight_sum = sum([position[2] for position in etf_holdings])
    portfolio_weight_sum = sum([holding.portfolio_percentage for holding in holdings])
    for etf_position in etf_holdings:
        etf_position_symbol = etf_position[0]
        etf_position_weight = etf_position[2]
        for holding in holdings:
            if etf_position_symbol in holding.tickers:
                shares_in_common.append(etf_position_symbol)
                portfolio_position_weight = holding.portfolio_percentage
                ind_overlap = min(etf_position_weight, portfolio_position_weight)
                individual_overlaps.append(ind_overlap)
                # overlap_sum += ind_overlap
    total_overlap_percentage = (
        2 * (sum(individual_overlaps)) / (etf_weight_sum + portfolio_weight_sum)
    )

    return shares_in_common, total_overlap_percentage


def get_lyxor_fund_data(url):
    response = requests.get(url)
    r_content = response.content

    return parse_lyxor_xls(r_content)


def get_ishares_fund_data(url):
    response = requests.get(url)
    wrapper = list(csv.reader(response.text.strip().split("\n")))

    return parse_ishares_csv(wrapper)


def get_ark_fund_data(url):
    scraper = cloudscraper.create_scraper()
    pdf_content = scraper.get(url).content

    return parse_ark_pdf(pdf_content)


def get_fund_data(issuer, url):
    if issuer == "iShares":
        fund_data = get_ishares_fund_data(url)
    elif issuer == "ARK":
        fund_data = get_ark_fund_data(url)
    elif issuer == "Lyxor":
        fund_data = get_lyxor_fund_data(url)

    return fund_data


def get_matching_etfs(holdings):
    matching_etfs = {}
    for etf_ticker in tqdm(ETF_LIST):
        etf_data = get_fund_data(
            ETF_LIST[etf_ticker]["issuer"], ETF_LIST[etf_ticker]["url"]
        )
        overlapping = calculate_overlapping_percentage(etf_data, holdings)
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
            print("Overlapping holdings:", sorted_etfs[etf_ticker][0])
            print("----")
        else:
            no_overlap.append(etf_ticker)
    print("No overlap found in:")
    for no_overlap_ticker in no_overlap:
        print(f"{no_overlap_ticker} - {ETF_LIST[no_overlap_ticker]['name']}")

def collect_all_tickers_from_isin(isin):
    FIGI_URL = 'https://api.openfigi.com/v3/mapping'
    FIGI_HEADERS = {
        'Content-Type':'application/json'
    }
    FIGI_PAYLOAD = '[{"idType":"ID_ISIN","idValue":"'+ isin +'"}]'

    r = requests.post(FIGI_URL, headers=FIGI_HEADERS, data=FIGI_PAYLOAD)

    json_data = r.json()[0]['data']

    company = json_data[0]['name']
    all_tickers = []
    main_ticker = ""

    for i in range(len(json_data)):
        ticker = json_data[i]['ticker']
        if "/" in ticker:
            ticker = ticker.replace("/", ".")

        if json_data[i]['exchCode'] == 'US':
            main_ticker = ticker
        all_tickers.append(ticker)

    return company, list(set(all_tickers)), main_ticker

# Get stock quote from yahoo
def get_stock_quote(ticker, av_key):
    URL = "https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol="+ ticker +"&apikey=" + av_key
    r = requests.get(URL)
    quote = float(r.json()["Global Quote"]["05. price"])
    return quote

def calculate_holding_percentage(holdings):
    portfolio_sum = 0
    for holding in holdings:
        portfolio_sum += holding.quantity * holding.price
    
    for holding in holdings:
        holding.portfolio_percentage = holding.quantity * holding.price / portfolio_sum * 100
    
    return holdings


if __name__ == "__main__":
    pp = pprint.PrettyPrinter(indent=4)
    load_dotenv()

    av_key = os.getenv("ALPHAVANTAGE_KEY")

    holdings = []
    collecting_tickers_successful = True

    portfolio_data_yaml = ""

    with open("portfolio.yml") as f:
        portfolio_data_yaml = yaml.load(f, Loader=SafeLoader)

    p_bar = tqdm(portfolio_data_yaml, desc="Collecting tickers from ISINs")

    for isin in p_bar:
        try:
            company_name, tickers, main_ticker = collect_all_tickers_from_isin(isin)
            p_bar.set_postfix_str(f"Collected {company_name}")
        except json.decoder.JSONDecodeError:
            print("Too many requests. Try again later or increase sleep.")
            collecting_tickers_successful = False
            break

        stock_quote = get_stock_quote(main_ticker, av_key)
        holding = Holding(company_name, isin, main_ticker, tickers, portfolio_data_yaml[isin], stock_quote)
        holdings.append(holding)
        sleep(12)
    
    if collecting_tickers_successful:
        holdings = calculate_holding_percentage(holdings)
        matching_etfs = get_matching_etfs(holdings)
        beautiful_output(matching_etfs)