"""
Model — Multiple Linear Regression for dosage estimation.
Outputs a range (min-max) based on prediction ± residual std.
"""

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_absolute_error
from typing import Dict, Tuple

from src.preprocessor import DosagePreprocessor
from src.data_generator import generate_dataset


class DosageModel:
    """MLR-based dosage estimator with range output."""

    def __init__(self):
        self.model = LinearRegression()
        self.preprocessor = DosagePreprocessor()
        self.residual_std: float = 0.0
        self.metrics: Dict[str, float] = {}
        self.is_trained = False

    def train(self, df: pd.DataFrame = None, test_size: float = 0.2) -> Dict[str, float]:
        """Train the model. Returns metrics dict."""
        if df is None:
            df = generate_dataset()

        X, y = self.preprocessor.fit_transform(df)
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42
        )

        self.model.fit(X_train, y_train)

        # Calculate residual std on training set for range estimation
        train_preds = self.model.predict(X_train)
        self.residual_std = np.std(y_train - train_preds)

        # Test metrics
        test_preds = self.model.predict(X_test)
        self.metrics = {
            "r2_score": round(r2_score(y_test, test_preds), 4),
            "mae": round(mean_absolute_error(y_test, test_preds), 2),
            "residual_std": round(self.residual_std, 2),
            "train_samples": len(X_train),
            "test_samples": len(X_test),
        }
        self.is_trained = True
        return self.metrics

    def predict_range(
        self,
        age: int,
        weight: float,
        gender: str,
        severity: str,
        medicine_type: str,
        confidence_multiplier: float = 1.5,
    ) -> Tuple[float, float, float]:
        """
        Predict dosage range.
        Returns (min_mg, predicted_mg, max_mg).
        """
        if not self.is_trained:
            raise RuntimeError("Model not trained yet.")

        X_input = self.preprocessor.transform_input(
            age, weight, gender, severity, medicine_type
        )
        predicted = self.model.predict(X_input)[0]

        margin = self.residual_std * confidence_multiplier
        min_mg = max(50, round(predicted - margin, 1))
        max_mg = round(predicted + margin, 1)
        predicted = round(predicted, 1)

        return min_mg, predicted, max_mg

    def get_feature_importance(self) -> pd.DataFrame:
        """Return feature importance (absolute coefficients)."""
        if not self.is_trained:
            raise RuntimeError("Model not trained yet.")

        coefs = self.model.coef_
        names = self.preprocessor.feature_names
        importance = pd.DataFrame({
            "feature": names,
            "coefficient": coefs,
            "abs_importance": np.abs(coefs),
        }).sort_values("abs_importance", ascending=False)

        return importance

    def get_formula_string(self) -> str:
        """Return the regression formula as a readable string."""
        if not self.is_trained:
            return "Model not trained."

        intercept = round(self.model.intercept_, 2)
        terms = []
        for name, coef in zip(self.preprocessor.feature_names, self.model.coef_):
            sign = "+" if coef >= 0 else "-"
            terms.append(f"{sign} {abs(round(coef, 2))}×{name}")

        formula = f"dosage = {intercept} " + " ".join(terms)
        return formula
