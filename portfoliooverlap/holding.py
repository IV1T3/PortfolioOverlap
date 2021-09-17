from dataclasses import dataclass

@dataclass
class Holding:
    name: str
    isin: str
    main_ticker: str
    tickers: list
    quantity: float
    price: float

    portfolio_percentage: float = 0.0

    
    