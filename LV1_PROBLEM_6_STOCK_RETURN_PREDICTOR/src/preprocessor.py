"""
preprocessor.py — Feature engineering for stock return prediction.
Creates LAGGED rolling averages, momentum indicators, and volume trends.
All features use data from the previous day to avoid leakage.
"""

import pandas as pd
import numpy as np


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Takes raw OHLCV data and adds lagged engineered features.
    All features are shifted by 1 day (use yesterday's info to predict today).
    Returns a clean DataFrame with no NaN rows.
    """
    data = df.copy()

    # ── Daily return % ──
    data["Daily_Return"] = data["Close"].pct_change() * 100

    # ── Rolling averages (on Close) ──
    data["SMA_5"] = data["Close"].rolling(window=5).mean()
    data["SMA_20"] = data["Close"].rolling(window=20).mean()
    data["SMA_50"] = data["Close"].rolling(window=50).mean()

    # ── Price momentum ──
    data["Momentum_5"] = data["Close"] - data["Close"].shift(5)
    data["Momentum_20"] = data["Close"] - data["Close"].shift(20)

    # ── Volatility (rolling std of returns) ──
    data["Volatility_10"] = data["Daily_Return"].rolling(window=10).std()
    data["Volatility_20"] = data["Daily_Return"].rolling(window=20).std()

    # ── Volume trend ──
    data["Vol_SMA_10"] = data["Volume"].rolling(window=10).mean()
    data["Vol_Ratio"] = data["Volume"] / data["Vol_SMA_10"]

    # ── RSI (Relative Strength Index — 14 day) ──
    delta = data["Close"].diff()
    gain = delta.where(delta > 0, 0).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss.replace(0, np.nan)
    data["RSI_14"] = 100 - (100 / (1 + rs))

    # ── Price relative to SMAs (ratio) ──
    data["Price_to_SMA20"] = data["Close"] / data["SMA_20"]
    data["Price_to_SMA50"] = data["Close"] / data["SMA_50"]

    # ── Day index (trend component for polynomial) ──
    data["Day_Index"] = np.arange(len(data))

    # ══ LAG all features by 1 day to prevent leakage ══
    # We predict today's Close using YESTERDAY's indicators
    feature_cols_to_lag = [
        "SMA_5", "SMA_20", "SMA_50",
        "Momentum_5", "Momentum_20",
        "Volatility_10", "Volatility_20",
        "Vol_Ratio", "RSI_14",
        "Price_to_SMA20", "Price_to_SMA50",
        "Daily_Return",
    ]
    for col in feature_cols_to_lag:
        data[f"Lag_{col}"] = data[col].shift(1)

    # Drop NaN rows created by rolling windows + lag
    data = data.dropna().reset_index(drop=True)

    # Recalculate day index after dropping NaNs
    data["Day_Index"] = np.arange(len(data))

    return data


def get_feature_columns() -> list:
    """Return the list of LAGGED feature columns used for prediction."""
    return [
        "Day_Index",
        "Lag_SMA_5",
        "Lag_SMA_20",
        "Lag_SMA_50",
        "Lag_Momentum_5",
        "Lag_Momentum_20",
        "Lag_Volatility_10",
        "Lag_Volatility_20",
        "Lag_Vol_Ratio",
        "Lag_RSI_14",
        "Lag_Price_to_SMA20",
        "Lag_Price_to_SMA50",
        "Lag_Daily_Return",
    ]


def prepare_future_features(data: pd.DataFrame, days_ahead: int) -> pd.DataFrame:
    """
    Create feature rows for future prediction days.
    Uses last known lagged values + extrapolated Day_Index.
    """
    last_row = data.iloc[-1]
    last_day_index = last_row["Day_Index"]

    feature_cols = get_feature_columns()
    future_rows = []

    for i in range(1, days_ahead + 1):
        row = {}
        row["Day_Index"] = last_day_index + i

        # Carry forward last known lagged values
        for col in feature_cols:
            if col != "Day_Index":
                row[col] = last_row[col]

        future_rows.append(row)

    return pd.DataFrame(future_rows)
