"""
Preprocessor — encodes categorical features + scales numerical ones.
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, LabelEncoder
from typing import Tuple, Dict


class DosagePreprocessor:
    """Handles encoding + scaling for the dosage model."""

    def __init__(self):
        self.scaler = StandardScaler()
        self.label_encoders: Dict[str, LabelEncoder] = {}
        self.categorical_cols = ["medicine_type", "gender", "severity"]
        self.numerical_cols = ["age", "weight_kg"]
        self.is_fitted = False

    def fit_transform(self, df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """Fit on training data and return (X, y)."""
        df_processed = df.copy()

        # Encode categoricals
        for col in self.categorical_cols:
            le = LabelEncoder()
            df_processed[col] = le.fit_transform(df_processed[col])
            self.label_encoders[col] = le

        # Feature matrix
        feature_cols = self.numerical_cols + self.categorical_cols
        X = df_processed[feature_cols].values
        y = df_processed["dosage_mg"].values

        # Scale features
        X = self.scaler.fit_transform(X)
        self.is_fitted = True

        return X, y

    def transform_input(
        self,
        age: int,
        weight: float,
        gender: str,
        severity: str,
        medicine_type: str,
    ) -> np.ndarray:
        """Transform a single user input for prediction."""
        if not self.is_fitted:
            raise RuntimeError("Preprocessor not fitted yet. Train the model first.")

        encoded = {
            "age": age,
            "weight_kg": weight,
            "medicine_type": self.label_encoders["medicine_type"].transform([medicine_type])[0],
            "gender": self.label_encoders["gender"].transform([gender])[0],
            "severity": self.label_encoders["severity"].transform([severity])[0],
        }

        row = np.array([[encoded["age"], encoded["weight_kg"],
                         encoded["medicine_type"], encoded["gender"],
                         encoded["severity"]]])
        return self.scaler.transform(row)

    @property
    def feature_names(self):
        return self.numerical_cols + self.categorical_cols
