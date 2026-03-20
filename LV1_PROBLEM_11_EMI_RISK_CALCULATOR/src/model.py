"""
Ridge Regression model — predicts EMI risk score (0-100).
"""

import numpy as np
from sklearn.linear_model import Ridge

from src.preprocessor import (
    FEATURE_COLS,
    TARGET_COL,
    get_scaler,
    load_data,
    prepare_input,
    scale_features,
)


def calculate_emi(principal: float, annual_rate: float, tenure_months: int) -> float:
    """Standard EMI formula: P * r * (1+r)^n / ((1+r)^n - 1)"""
    if annual_rate == 0:
        return principal / tenure_months
    r = annual_rate / (12 * 100)
    emi = principal * r * (1 + r) ** tenure_months / ((1 + r) ** tenure_months - 1)
    return round(emi, 2)


def train_model():
    """Train Ridge Regression on synthetic dataset. Returns (model, scaler)."""
    df = load_data()
    scaler = get_scaler(df)

    X = scale_features(scaler, df[FEATURE_COLS].values)
    y = df[TARGET_COL].values

    model = Ridge(alpha=1.0)
    model.fit(X, y)

    return model, scaler


def predict_risk(
    model: Ridge,
    scaler,
    income: float,
    expenses: float,
    loan_amount: float,
    tenure: int,
    interest_rate: float,
) -> dict:
    """
    Predict risk score and compute EMI + debt-to-income ratio.
    Returns dict with emi, risk_score, risk_label, dti_ratio.
    """
    emi = calculate_emi(loan_amount, interest_rate, tenure)

    raw_input = prepare_input(income, expenses, loan_amount, tenure, interest_rate)
    scaled_input = scale_features(scaler, raw_input)
    risk_score = float(np.clip(model.predict(scaled_input)[0], 0, 100))

    dti_ratio = (emi / income) * 100 if income > 0 else 100.0

    # Risk label
    if risk_score < 33:
        risk_label = "Low"
    elif risk_score < 66:
        risk_label = "Medium"
    else:
        risk_label = "High"

    return {
        "emi": round(emi, 2),
        "risk_score": round(risk_score, 2),
        "risk_label": risk_label,
        "dti_ratio": round(dti_ratio, 2),
    }
