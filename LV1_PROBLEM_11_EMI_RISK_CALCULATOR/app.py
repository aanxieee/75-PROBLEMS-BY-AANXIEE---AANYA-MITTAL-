"""
Day 11/75 — EMI Risk Calculator | Ridge Regression | Fintech
"""

import streamlit as st
from src.model import train_model, predict_risk

# ── Page Config ──────────────────────────────────────────────
st.set_page_config(
    page_title="EMI Risk Calculator",
    page_icon="🏦",
    layout="centered",
)

# ── Custom CSS ───────────────────────────────────────────────
st.markdown(
    """
    <style>
    .risk-low { color: #22c55e; font-size: 2rem; font-weight: 800; }
    .risk-medium { color: #f59e0b; font-size: 2rem; font-weight: 800; }
    .risk-high { color: #ef4444; font-size: 2rem; font-weight: 800; }
    .emi-amount { font-size: 2.2rem; font-weight: 800; color: #3b82f6; }
    .metric-card {
        background: #f8fafc;
        border-radius: 12px;
        padding: 1.2rem;
        text-align: center;
        border: 1px solid #e2e8f0;
    }
    .disclaimer {
        background: #fef3c7;
        border-left: 4px solid #f59e0b;
        padding: 0.8rem 1rem;
        border-radius: 0 8px 8px 0;
        font-size: 0.85rem;
        margin-top: 1rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ── Load Model (cached) ─────────────────────────────────────
@st.cache_resource
def load_model():
    return train_model()


model, scaler = load_model()


# ── Header ───────────────────────────────────────────────────
st.title("🏦 EMI Risk Calculator")
st.caption("Day 11/75 — 75 Hard Engineer Edition | Ridge Regression × Fintech")

st.markdown(
    '<div class="disclaimer">'
    "⚠️ <b>Disclaimer:</b> This tool uses a synthetic dataset and Ridge Regression "
    "for educational purposes only. <b>Not financial advice.</b> "
    "Consult a certified financial advisor for real loan decisions."
    "</div>",
    unsafe_allow_html=True,
)

st.divider()

# ── Section 1: EMI Risk Check ───────────────────────────────
st.header("📊 EMI Risk Check")

col1, col2 = st.columns(2)

with col1:
    income = st.number_input(
        "Monthly Income (₹)", min_value=5000, max_value=10_000_000,
        value=60000, step=5000, format="%d",
    )
    expenses = st.number_input(
        "Monthly Expenses (₹)", min_value=0, max_value=10_000_000,
        value=25000, step=2000, format="%d",
    )
    loan_amount = st.number_input(
        "Loan Amount (₹)", min_value=10000, max_value=100_000_000,
        value=500000, step=50000, format="%d",
    )

with col2:
    tenure = st.selectbox(
        "Tenure (months)",
        options=[6, 12, 24, 36, 48, 60, 72, 84, 120, 180, 240],
        index=3,
    )
    interest_rate = st.slider(
        "Interest Rate (%)", min_value=5.0, max_value=25.0,
        value=10.5, step=0.25,
    )

if st.button("🔍 Check EMI Risk", type="primary", use_container_width=True):
    result = predict_risk(model, scaler, income, expenses, loan_amount, tenure, interest_rate)

    st.divider()

    # EMI Amount
    m1, m2, m3 = st.columns(3)

    with m1:
        st.markdown(
            '<div class="metric-card">'
            "<p style='margin:0;color:#64748b;font-size:0.85rem;'>Monthly EMI</p>"
            f"<p class='emi-amount'>₹{result['emi']:,.2f}</p>"
            "</div>",
            unsafe_allow_html=True,
        )

    with m2:
        css_class = f"risk-{result['risk_label'].lower()}"
        st.markdown(
            '<div class="metric-card">'
            "<p style='margin:0;color:#64748b;font-size:0.85rem;'>Risk Score</p>"
            f"<p class='{css_class}'>{result['risk_score']}/100</p>"
            f"<p style='margin:0;font-weight:600;'>{result['risk_label']} Risk</p>"
            "</div>",
            unsafe_allow_html=True,
        )

    with m3:
        dti_color = "#22c55e" if result["dti_ratio"] < 40 else (
            "#f59e0b" if result["dti_ratio"] < 60 else "#ef4444"
        )
        st.markdown(
            '<div class="metric-card">'
            "<p style='margin:0;color:#64748b;font-size:0.85rem;'>Debt-to-Income</p>"
            f"<p style='font-size:2rem;font-weight:800;color:{dti_color};'>"
            f"{result['dti_ratio']}%</p>"
            "</div>",
            unsafe_allow_html=True,
        )

    # Quick interpretation
    if result["risk_label"] == "Low":
        st.success("✅ This EMI looks comfortable for your income level.")
    elif result["risk_label"] == "Medium":
        st.warning("⚠️ EMI is manageable but leaves a tight margin. Plan carefully.")
    else:
        st.error("🚨 High risk — EMI takes a large chunk of income. Reconsider terms.")

st.divider()

# ── Section 2: How It Works ─────────────────────────────────
st.header("🧠 How It Works")

st.markdown(
    """
**Ridge Regression** is a regularized version of Linear Regression.
It adds an L2 penalty (alpha) to prevent the model from overfitting — especially
useful when working with small or synthetic datasets like ours.

**What the model learns:**

It maps five input features — income, expenses, loan amount, tenure, and interest
rate — to a risk score between 0 and 100. The risk score is derived from
the **debt-to-income (DTI) ratio**: how much of your monthly income goes toward EMI.

| Risk Level | Score Range | Meaning |
|:-----------|:-----------|:--------|
| 🟢 Low | 0 – 32 | EMI is well within budget |
| 🟡 Medium | 33 – 65 | Manageable but needs planning |
| 🔴 High | 66 – 100 | EMI may strain finances |

**About the Dataset:**

- 500 synthetic rows generated with `numpy`
- Realistic ranges for Indian income levels (₹20k–₹2L/month)
- Loan amounts ₹50k to ₹50L, tenures 6–240 months
- Risk score = `clip(EMI / Income, 0, 1) × 100 + noise`
- **No real user data** is used anywhere
"""
)

st.markdown(
    '<div class="disclaimer">'
    "⚠️ <b>Reminder:</b> This is a synthetic model for learning purposes. "
    "Real credit risk assessment uses credit scores, employment history, "
    "collateral, and many more factors. <b>Always consult a professional.</b>"
    "</div>",
    unsafe_allow_html=True,
)

# ── Footer ───────────────────────────────────────────────────
st.divider()
st.caption("Day 11/75 — 75 Hard Engineer Edition 🔥 | Built by Aanya Mittal")
