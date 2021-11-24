from dataclasses import dataclass


@dataclass
class Holding:
    name: str
    isin: str
    main_ticker: str
    tickers: list
    quantity: float
    price: float
    is_etf: bool

    portfolio_percentage: float = 0.0
    etf_resolved: bool = False
