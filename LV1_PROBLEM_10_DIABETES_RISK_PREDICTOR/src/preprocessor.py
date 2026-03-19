"""
Preprocessor — loads Pima dataset, scales features, maps user inputs.
Features used: Glucose, BloodPressure, BMI, DiabetesPedigreeFunction, Age
"""

import os
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler


# 5 features we actually use from the dataset
FEATURE_COLS = ["Glucose", "BloodPressure", "BMI", "DiabetesPedigreeFunction", "Age"]
TARGET_COL = "Outcome"


def load_data():
    """Load and clean the Pima Indians Diabetes dataset."""
    data_path = os.path.join(os.path.dirname(__file__), "..", "data", "diabetes.csv")
    df = pd.read_csv(data_path)

    # Replace 0s with NaN for columns where 0 is not possible, then fill with median
    zero_invalid = ["Glucose", "BloodPressure", "BMI"]
    for col in zero_invalid:
        df[col] = df[col].replace(0, np.nan)
        df[col] = df[col].fillna(df[col].median())

    return df


def get_scaler_and_data():
    """Return fitted scaler, X_scaled, y arrays."""
    df = load_data()
    X = df[FEATURE_COLS].values
    y = df[TARGET_COL].values

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    return scaler, X_scaled, y


def prepare_user_input(glucose, blood_pressure, bmi, family_history, age, scaler):
    """
    Convert user form inputs into a scaled feature array.
    Family history (yes/no) → mapped to DiabetesPedigreeFunction:
      Yes → 0.63 (75th percentile of dataset)
      No  → 0.24 (25th percentile of dataset)
    """
    dpf = 0.63 if family_history else 0.24

    raw = np.array([[glucose, blood_pressure, bmi, dpf, age]])
    scaled = scaler.transform(raw)
    return scaled
