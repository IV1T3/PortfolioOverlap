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

Currently, 31 of the most popular ETFs from iShares, ARK and Lyxor are supported:

| ETF                                      | Ticker |
| ---------------------------------------- | ------ |
| ARK INNOVATION ETF                       | ARKK   |
| ARK Autonomous Technology & Robotics ETF | ARKQ   |
| ...                                      | ...    |
| iShares Core MSCI World UCITS ETF        | EUNL   |
| ...                                      | ...    |
| Lyxor MSCI World Energy TR UCITS ETF     | LYPC   |
| ...                                      | ...    |

First, customize the file `portfoliooverlap/portfolio.py` to resemble your stock portfolio such as:

```python
PORTFOLIO_DATA = {
    "AAPL": 25.0,
    "MSFT": 25.0,
    "AMZN": 25.0,
    "TSLA": 25.0,
}
```

Then get insight into weighted overlaps by running

```console
$ python3 portfoliooverlap/main.py
```
