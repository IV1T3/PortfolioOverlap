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

Currently, 29 of the most popular ETFs from iShares and ARK are added:

| ETF                                      | Ticker |
| ---------------------------------------- | ------ |
| ARK INNOVATION ETF                       | ARKK   |
| ARK Autonomous Technology & Robotics ETF | ARKQ   |
| ...                                      | ...    |
| iShares Core MSCI World UCITS ETF        | EUNL   |
| ...                                      | ...    |

First, customize the file portfolio.py to resemble your stock portfolio.
Then get insight into weighted overlaps by running

```console
$ python3 etf_overlap.py
```
