# PortfolioOverlap

_PortfolioOverlap_ is a CLI tool that helps you to compare the weighted holdings of your stock portfolio with popular Exchange Traded Funds (ETFs) to distinguish overlaps. It also features the resolution of ETFs into their individual components to help you to understand the underlying components of the ETF and find possible risk concentrations.

Currently, 3 ETFs of ARK Invest are supported:

| ETF                                      | Ticker |
| ---------------------------------------- | ------ |
| ARK INNOVATION ETF                       | ARKK   |
| ARK Autonomous Technology & Robotics ETF | ARKQ   |
| ARK Next Generation Internet ETF         | ARKW   |

[//]: # (| ...                                      | ...    |)
[//]: # (| iShares Core MSCI World UCITS ETF        | EUNL   |)
[//]: # (| ...                                      | ...    |)
[//]: # (| Lyxor MSCI World Energy TR UCITS ETF     | LYPC   |)
[//]: # (| ...                                      | ...    |)
## Installation

The Python _virtualenv_ is recommended to use as a Python environment. This project requires Python3.

```console
git clone https://github.com/IV1T3/PortfolioOverlap.git
cd PortfolioOverlap
virtualenv venv
source venv/bin/activate
pip3 install -r requirements.txt
```

## How to use

First, insert your portfolio into the file `portfolio.yml` in the format ```ISIN: number of shares held```. It is recommended to append the ticker symbol as a comment to the end of the line to make it easier identifying the equity. It is possible to add common stocks and ETFs to the portfolio.

```yaml
US0378331005: 1.0 # AAPL
US5949181045: 2.0 # MSFT
US0231351067: 3.0 # AMZN
US88160R1014: 4.0 # TSLA
US00214Q1040: 5.0 # ARKK (ETF)
```

The tool also uses the AlphaVantage API to fetch the current price of the stocks in your portfolio. To use the API, you need to get a free API key at [AlphaVantage](https://www.alphavantage.co/support/#api-key). In the root directory of the project, create a file named `.env` and add your API key as follows:
```console
ALPHAVANTAGE_KEY = "API_KEY"
```

Then, run the tool

```console
python3 portfoliooverlap/main.py
```

Using the portfolio above yields
the following insights

```
ETFs sorted by weighted overlap in descending order
------
ARK INNOVATION ETF
Overlap: 13.2571%
---
Top 5 overlapping holdings:
1. TESLA INC
2. COINBASE GLOBAL INC
3. UNITY SOFTWARE INC
4. TELADOC HEALTH INC
5. ROKU INC
------------
------------
ARK Next Generation Internet ETF
Overlap: 12.8671%
---
Top 5 overlapping holdings:
1. TESLA INC
2. COINBASE GLOBAL INC
3. TWITTER INC
4. SHOPIFY INC CLASS
5. TELADOC HEALTH INC
------------
------------
ARK Autonomous Technology & Robotics ETF
Overlap: 12.3445%
---
Top 5 overlapping holdings:
1. TESLA INC
2. TRIMBLE INC
3. UIPATH INC CLASS
4. UNITY SOFTWARE INC
5. IRIDIUM COMMUNICATIONS INC

------------
------------
```
