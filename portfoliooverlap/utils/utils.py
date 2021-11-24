import dateparser

import yfinance as yf

from datetime import datetime


def chunks(lst, n):
    return [lst[i : i + n] for i in range(0, len(lst), n)]


def check_float(potential_float):
    try:
        float(potential_float)
        return True
    except ValueError:
        return False


def format_date(date):
    return datetime.timestamp(dateparser.parse(date))


def get_quote_type(ticker):
    """
    Returns the quote type of the ticker: 'STOCK' or 'ETF'.
    """
    stock = yf.Ticker(ticker)
    long_name = stock.info["longName"]
    if "ETF" in long_name:
        type = "ETF"
    else:
        type = "STOCK"
    return type
