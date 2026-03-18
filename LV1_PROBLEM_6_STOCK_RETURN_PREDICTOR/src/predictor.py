"""
predictor.py — Polynomial Regression model for stock return prediction.
Uses PolynomialFeatures + LinearRegression from scikit-learn.
Includes train/test split and confidence interval estimation.
"""

import numpy as np
import pandas as pd
from sklearn.preprocessing import PolynomialFeatures, StandardScaler
from sklearn.linear_model import Ridge
from sklearn.pipeline import Pipeline
from sklearn.metrics import r2_score, mean_absolute_error


class StockPredictor:
    """Polynomial Regression predictor for stock closing prices."""

    def __init__(self, degree: int = 2):
        self.degree = degree
        self.scaler = StandardScaler()
        # Ridge regression to prevent overfitting with polynomial features
        self.pipeline = Pipeline([
            ("poly", PolynomialFeatures(degree=degree, include_bias=False)),
            ("reg", Ridge(alpha=1.0)),
        ])
        self.is_fitted = False
        self.train_residual_std = None

    def fit(self, X: pd.DataFrame, y: pd.Series,
            test_split: float = 0.2) -> dict:
        """
        Train the model with a time-based train/test split.
        Returns dict with training and test metrics.
        """
        split_idx = int(len(X) * (1 - test_split))

        X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
        y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]

        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)

        # Fit pipeline on training data only
        self.pipeline.fit(X_train_scaled, y_train)
        self.is_fitted = True

        # Training metrics
        y_train_pred = self.pipeline.predict(X_train_scaled)
        train_residuals = y_train - y_train_pred
        self.train_residual_std = np.std(train_residuals)

        # Test metrics
        y_test_pred = self.pipeline.predict(X_test_scaled)

        metrics = {
            "train_r2": round(r2_score(y_train, y_train_pred), 4),
            "test_r2": round(r2_score(y_test, y_test_pred), 4),
            "train_mae": round(mean_absolute_error(y_train, y_train_pred), 2),
            "test_mae": round(mean_absolute_error(y_test, y_test_pred), 2),
            "residual_std": round(self.train_residual_std, 2),
            "degree": self.degree,
            "n_train": len(y_train),
            "n_test": len(y_test),
            "split_idx": split_idx,
        }

        return metrics

    def predict(self, X: pd.DataFrame, confidence: float = 0.95) -> dict:
        """
        Predict closing prices with confidence intervals.
        Returns dict with predictions, upper, lower bounds.
        """
        if not self.is_fitted:
            raise ValueError("Model not fitted yet. Call fit() first.")

        X_scaled = self.scaler.transform(X)
        y_pred = self.pipeline.predict(X_scaled)

        # Confidence interval using residual std (approximate)
        z_scores = {0.90: 1.645, 0.95: 1.96, 0.99: 2.576}
        z = z_scores.get(confidence, 1.96)

        margin = z * self.train_residual_std

        return {
            "predicted": y_pred,
            "upper": y_pred + margin,
            "lower": y_pred - margin,
            "margin": margin,
        }

    def predict_returns(self, current_price: float,
                        predicted_prices: np.ndarray) -> dict:
        """
        Calculate predicted return % from current price.
        """
        final_price = predicted_prices[-1]
        return_pct = ((final_price - current_price) / current_price) * 100

        return {
            "current_price": round(current_price, 2),
            "predicted_price": round(final_price, 2),
            "return_pct": round(return_pct, 2),
            "direction": "📈 Bullish" if return_pct > 0 else "📉 Bearish",
        }


def calculate_sip_projection(monthly_amount: float,
                              months: int,
                              predicted_annual_return: float) -> dict:
    """
    Project SIP value based on predicted annual return.
    Uses standard SIP formula with monthly compounding.
    """
    monthly_rate = predicted_annual_return / 100 / 12
    total_invested = monthly_amount * months

    if abs(monthly_rate) < 1e-10:
        future_value = total_invested
    else:
        future_value = monthly_amount * (
            ((1 + monthly_rate) ** months - 1) / monthly_rate
        ) * (1 + monthly_rate)

    gains = future_value - total_invested

    # Month-by-month breakdown for chart
    breakdown = []
    cumulative_invested = 0
    cumulative_value = 0

    for m in range(1, months + 1):
        cumulative_invested += monthly_amount
        cumulative_value = (cumulative_value + monthly_amount) * (1 + monthly_rate)
        breakdown.append({
            "month": m,
            "invested": round(cumulative_invested, 2),
            "value": round(cumulative_value, 2),
        })

    return {
        "monthly_amount": monthly_amount,
        "months": months,
        "annual_return_pct": round(predicted_annual_return, 2),
        "total_invested": round(total_invested, 2),
        "future_value": round(future_value, 2),
        "gains": round(gains, 2),
        "gain_pct": round((gains / total_invested) * 100, 2) if total_invested > 0 else 0,
        "breakdown": breakdown,
    }
