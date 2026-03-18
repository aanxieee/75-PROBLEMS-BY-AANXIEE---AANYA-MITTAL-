"""
data_fetcher.py — Fetch historical stock/index data via yfinance.
"""

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta


# Quick-pick presets for Indian market
PRESETS = {
    "NIFTY 50": "^NSEI",
    "SENSEX": "^BSEIN",
    "Reliance": "RELIANCE.NS",
    "TCS": "TCS.NS",
    "Infosys": "INFY.NS",
    "HDFC Bank": "HDFCBANK.NS",
    "ITC": "ITC.NS",
}


def fetch_stock_data(ticker: str, period_years: int = 3) -> pd.DataFrame:
    """
    Fetch historical OHLCV data for a given ticker.
    Returns a cleaned DataFrame with Date as column (not index).
    """
    end_date = datetime.today()
    start_date = end_date - timedelta(days=period_years * 365)

    stock = yf.Ticker(ticker)
    df = stock.history(start=start_date.strftime("%Y-%m-%d"),
                       end=end_date.strftime("%Y-%m-%d"))

    if df.empty:
        return pd.DataFrame()

    df = df.reset_index()

    # Normalize column names (yfinance sometimes varies)
    df.columns = [col.strip().title() for col in df.columns]

    # Keep only what we need
    keep_cols = ["Date", "Open", "High", "Low", "Close", "Volume"]
    df = df[[c for c in keep_cols if c in df.columns]].copy()

    # Remove timezone info from Date
    df["Date"] = pd.to_datetime(df["Date"]).dt.tz_localize(None)

    df = df.sort_values("Date").reset_index(drop=True)
    return df


def get_stock_info(ticker: str) -> dict:
    """Return basic info about the stock/index."""
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        return {
            "name": info.get("shortName", info.get("longName", ticker)),
            "currency": info.get("currency", "INR"),
            "market": info.get("exchange", "NSE"),
            "current_price": info.get("currentPrice",
                                      info.get("regularMarketPrice", None)),
            "52w_high": info.get("fiftyTwoWeekHigh", None),
            "52w_low": info.get("fiftyTwoWeekLow", None),
        }
    except Exception:
        return {"name": ticker, "currency": "INR", "market": "—"}
