import pandas as pd

from src.screener import screen


def test_screen_filters_change_and_query():
    rows = [
        {"type": "crypto", "symbol": "BTC", "name": "Bitcoin", "change_24h_pct": 8, "market_cap": 100},
        {"type": "stock", "symbol": "BBCA", "name": "BBCA", "change_24h_pct": 3, "market_cap": 200},
    ]
    result = screen(rows, min_change=5, query="btc")
    assert list(result["symbol"]) == ["BTC"]


def test_screen_empty_rows_returns_dataframe():
    result = screen([])
    assert isinstance(result, pd.DataFrame)
    assert result.empty
