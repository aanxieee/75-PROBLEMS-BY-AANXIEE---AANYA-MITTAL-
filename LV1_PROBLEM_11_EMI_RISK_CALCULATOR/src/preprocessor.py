"""
Preprocessor — StandardScaler for EMI risk features.
"""

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler


FEATURE_COLS = ["income", "expenses", "loan_amount", "tenure", "interest_rate"]
TARGET_COL = "risk_score"


def load_data(path: str = "data/emi_data.csv") -> pd.DataFrame:
    """Load the synthetic EMI dataset."""
    return pd.read_csv(path)


def get_scaler(df: pd.DataFrame) -> StandardScaler:
    """Fit and return a StandardScaler on training features."""
    scaler = StandardScaler()
    scaler.fit(df[FEATURE_COLS].values)
    return scaler


def scale_features(scaler: StandardScaler, features: np.ndarray) -> np.ndarray:
    """Transform raw features using a fitted scaler."""
    return scaler.transform(features)


def prepare_input(
    income: float,
    expenses: float,
    loan_amount: float,
    tenure: int,
    interest_rate: float,
) -> np.ndarray:
    """Pack user inputs into a 2D array for prediction."""
    return np.array([[income, expenses, loan_amount, tenure, interest_rate]])
