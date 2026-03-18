"""
Synthetic Dataset Generator for Medicine Dosage Estimator
Generates realistic-looking but fully artificial data.
⚠️ NOT real medical data — for educational purposes only.
"""

import numpy as np
import pandas as pd
import os

SEED = 42

# Base dosage rules (loosely inspired by general pharma guidelines)
# These are SYNTHETIC approximations, NOT real medical formulas
MEDICINE_PROFILES = {
    "Painkiller": {"base_mg": 200, "weight_factor": 1.5, "age_factor": -0.8, "severity_mult": {"Mild": 0.5, "Moderate": 1.0, "Severe": 1.5}},
    "Antibiotic": {"base_mg": 250, "weight_factor": 2.0, "age_factor": -0.5, "severity_mult": {"Mild": 0.6, "Moderate": 1.0, "Severe": 1.4}},
    "General OTC": {"base_mg": 325, "weight_factor": 1.0, "age_factor": -0.6, "severity_mult": {"Mild": 0.5, "Moderate": 1.0, "Severe": 1.3}},
}

GENDER_ADJUST = {"Male": 1.05, "Female": 0.95}


def generate_dataset(n_samples: int = 1500, seed: int = SEED) -> pd.DataFrame:
    """Generate synthetic dosage dataset."""
    rng = np.random.default_rng(seed)

    records = []
    for _ in range(n_samples):
        med = rng.choice(list(MEDICINE_PROFILES.keys()))
        profile = MEDICINE_PROFILES[med]

        age = int(rng.integers(18, 80))
        weight = round(rng.normal(70, 15), 1)
        weight = max(40, min(weight, 130))  # clamp
        gender = rng.choice(["Male", "Female"])
        severity = rng.choice(["Mild", "Moderate", "Severe"], p=[0.3, 0.45, 0.25])

        # Synthetic dosage formula
        dosage = (
            profile["base_mg"]
            + profile["weight_factor"] * weight
            + profile["age_factor"] * age
            + profile["base_mg"] * (profile["severity_mult"][severity] - 1)
        )
        dosage *= GENDER_ADJUST[gender]

        # Add realistic noise (±8%)
        noise = rng.normal(1.0, 0.08)
        dosage = round(dosage * noise, 1)
        dosage = max(50, dosage)  # minimum safe floor

        records.append({
            "medicine_type": med,
            "age": age,
            "weight_kg": weight,
            "gender": gender,
            "severity": severity,
            "dosage_mg": dosage,
        })

    return pd.DataFrame(records)


def save_dataset(df: pd.DataFrame, path: str = "data/dosage_data.csv"):
    """Save dataset to CSV."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    df.to_csv(path, index=False)
    print(f"✅ Dataset saved: {path} ({len(df)} rows)")


if __name__ == "__main__":
    df = generate_dataset()
    save_dataset(df)
    print(df.head(10))
    print(f"\nStats:\n{df.describe()}")
