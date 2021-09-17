# PortfolioOverlap

_PortfolioOverlap_ is a CLI tool that helps you to compare the weighted holdings of your stock portfolio with popular Exchange Traded Funds (ETFs) to distinguish overlaps.

## Installation

The Python _virtualenv_ is recommended to use as a Python environment. This project requires Python3.

```console
$ git clone https://github.com/IV1T3/PortfolioOverlap.git
$ cd PortfolioOverlap
$ virtualenv venv
$ source venv/bin/activate
$ pip3 install -r requirements.txt
```

## How to use

Currently, 68 of the most popular ETFs from iShares, ARK and Lyxor are supported:

| ETF                                      | Ticker |
| ---------------------------------------- | ------ |
| ARK INNOVATION ETF                       | ARKK   |
| ARK Autonomous Technology & Robotics ETF | ARKQ   |
| ...                                      | ...    |
| iShares Core MSCI World UCITS ETF        | EUNL   |
| ...                                      | ...    |
| Lyxor MSCI World Energy TR UCITS ETF     | LYPC   |
| ...                                      | ...    |

First, insert your stock portfolio into the file `portfolio.yml` in the format ```ISIN: number of shares held```. It is recommended to append the stock ticker symbol as a comment to the end of the line to make it easier identifying the stock.

```yaml
'US0378331005': 1.0 # AAPL
'US5949181045': 2.0 # MSFT
'US0231351067': 3.0 # AMZN
'US88160R1014': 4.0 # TSLA
```

The tool also uses the AlphaVantage API to fetch the current price of the stocks in your portfolio. To use the API, you need to get a free API key at [AlphaVantage](https://www.alphavantage.co/support/#api-key). In the root directory of the project, create a file named `.env` and add your API key as follows:
```console
ALPHAVANTAGE_KEY = "API_KEY"
```

Then, run the tool

```console
$ python3 portfoliooverlap/main.py
```

Using the portfolio above yields
the following insights

```
ETFs sorted by weighted overlap in descending order
----
iShares NASDAQ 100 UCITS ETF
Overlap: 17.1981%
Overlapping holdings: ['AAPL', 'MSFT', 'AMZN', 'TSLA']
----
iShares MSCI USA ESG Screened UCITS ETF
Overlap: 10.9532%
Overlapping holdings: ['AAPL', 'MSFT', 'AMZN', 'TSLA']
----
iShares Core S&P 500 UCITS ETF
Overlap: 10.8088%
Overlapping holdings: ['AAPL', 'MSFT', 'AMZN', 'TSLA']
----
...
```
