"""
KNN Model — trains on Pima dataset, returns risk level + probability.
"""

from sklearn.neighbors import KNeighborsClassifier
from src.preprocessor import get_scaler_and_data, prepare_user_input


# Risk thresholds
LOW_THRESHOLD = 0.35
HIGH_THRESHOLD = 0.65


def train_model(k=5):
    """Train KNN classifier and return model + scaler."""
    scaler, X_scaled, y = get_scaler_and_data()

    model = KNeighborsClassifier(n_neighbors=k, weights="distance", metric="minkowski")
    model.fit(X_scaled, y)

    return model, scaler


def predict_risk(model, scaler, glucose, blood_pressure, bmi, family_history, age):
    """
    Predict diabetes risk.
    Returns: (risk_label, probability_percent)
    """
    X_input = prepare_user_input(glucose, blood_pressure, bmi, family_history, age, scaler)

    proba = model.predict_proba(X_input)[0]
    diabetes_prob = proba[1]  # probability of class 1 (diabetic)

    if diabetes_prob < LOW_THRESHOLD:
        risk = "🟢 Low Risk"
    elif diabetes_prob < HIGH_THRESHOLD:
        risk = "🟡 Medium Risk"
    else:
        risk = "🔴 High Risk"

    return risk, round(diabetes_prob * 100, 1)
