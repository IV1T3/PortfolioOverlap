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

First, customize the file `portfolio.yml` to resemble your stock portfolio such as

```yaml
'US0378331005': 25.0 # AAPL
'US5949181045': 25.0 # MSFT
'US0231351067': 25.0 # AMZN
'US88160R1014': 25.0 # TSLA
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
iShares S&P 500 Information Technology Sector UCITS ETF
Overlap: 42.0621%
Overlapping holdings: ['AAPL', 'MSFT']
----
iShares NASDAQ 100 UCITS ETF
Overlap: 33.22%
Overlapping holdings: ['AAPL', 'MSFT', 'AMZN', 'TSLA']
----
iShares S&P 500 Paris-Aligned Climate UCITS ETF
Overlap: 19.3978%
Overlapping holdings: ['AAPL', 'MSFT', 'AMZN', 'TSLA']
----
...
```
