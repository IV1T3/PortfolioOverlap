from dataclasses import dataclass

@dataclass
class Stock:
    company: str
    isin: str
    tickers: list
    portfolio_percentage: float

    price: float = 0.0
    quantity: int = 0