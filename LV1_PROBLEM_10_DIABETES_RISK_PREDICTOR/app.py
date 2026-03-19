"""
🩺 Diabetes Risk Predictor — Day 10/75 Engineer Edition
KNN Classifier on Pima Indians Diabetes Dataset
"""

import streamlit as st
from src.model import train_model, predict_risk


# ── Page Config ──────────────────────────────────────────────
st.set_page_config(
    page_title="Diabetes Risk Predictor",
    page_icon="🩺",
    layout="centered",
)

# ── Disclaimer Banner ────────────────────────────────────────
st.warning(
    "⚠️ **Disclaimer:** This tool is for educational purposes only. "
    "It is **not** medical advice. Always consult a qualified doctor for diagnosis."
)

# ── Header ───────────────────────────────────────────────────
st.title("🩺 Diabetes Risk Predictor")
st.caption("KNN Classifier · Pima Indians Diabetes Dataset · Day 10/75")

# ── Load Model (cached) ─────────────────────────────────────
@st.cache_resource
def load_model():
    return train_model(k=5)

model, scaler = load_model()

# ── Tabs ─────────────────────────────────────────────────────
tab_risk, tab_about = st.tabs(["🔍 Risk Check", "ℹ️ About"])

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TAB 1 — Risk Check
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
with tab_risk:
    st.subheader("Enter your details")

    col1, col2 = st.columns(2)

    with col1:
        age = st.number_input("Age (years)", min_value=10, max_value=100, value=30, step=1)
        glucose = st.number_input(
            "Glucose Level (mg/dL)",
            min_value=40, max_value=300, value=120, step=1,
            help="Fasting blood glucose. Normal: 70–100 mg/dL",
        )
        family_history = st.selectbox(
            "Family History of Diabetes?",
            options=["No", "Yes"],
        )

    with col2:
        bmi = st.number_input(
            "BMI", min_value=10.0, max_value=60.0, value=25.0, step=0.1,
            help="Body Mass Index. Normal: 18.5–24.9",
        )
        blood_pressure = st.number_input(
            "Blood Pressure (mm Hg)",
            min_value=30, max_value=200, value=80, step=1,
            help="Diastolic blood pressure. Normal: ~80 mm Hg",
        )

    st.markdown("---")

    if st.button("🔎 Check My Risk", use_container_width=True, type="primary"):

        has_family = family_history == "Yes"
        risk_label, prob = predict_risk(model, scaler, glucose, blood_pressure, bmi, has_family, age)

        # Result card
        st.markdown("### Result")

        res_col1, res_col2 = st.columns(2)
        with res_col1:
            st.metric(label="Risk Level", value=risk_label)
        with res_col2:
            st.metric(label="Diabetes Probability", value=f"{prob}%")

        # Contextual tip
        if prob < 35:
            st.success("Your indicators look healthy! Keep up a balanced diet and regular exercise. 💪")
        elif prob < 65:
            st.info("Some indicators are borderline. Consider regular check-ups and lifestyle improvements. 🏥")
        else:
            st.error("Multiple indicators suggest elevated risk. Please consult a doctor soon. 🩺")

        st.caption("⚠️ This is a statistical estimate, not a diagnosis.")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TAB 2 — About
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
with tab_about:
    st.subheader("How It Works")

    st.markdown("""
**K-Nearest Neighbours (KNN)** is a simple machine learning algorithm that classifies
a new data point based on how its closest neighbours are classified.

**In this app:**
- We trained a KNN classifier (K=5) on the **Pima Indians Diabetes Dataset** (768 records).
- The model uses 5 features: **Glucose, Blood Pressure, BMI, Family History, and Age**.
- Your inputs are scaled using `StandardScaler`, then the model finds the 5 most similar
  patients and estimates your risk based on their outcomes.

**Risk Levels:**
- 🟢 **Low Risk** — probability < 35%
- 🟡 **Medium Risk** — probability 35–65%
- 🔴 **High Risk** — probability > 65%

**Dataset Source:**
[Pima Indians Diabetes Database](https://www.kaggle.com/datasets/uciml/pima-indians-diabetes-database)
— originally from the National Institute of Diabetes and Digestive and Kidney Diseases.
All patients are females, age ≥ 21, of Pima Indian heritage.

---
⚠️ **Disclaimer:** This tool provides a statistical estimate only. It is **not** a substitute
for professional medical advice, diagnosis, or treatment. Always consult your doctor.
""")

# ── Footer ───────────────────────────────────────────────────
st.markdown("---")
st.caption("Built by Aanya Mittal · Day 10/75 — 75 Hard Engineer Edition 🚀")
