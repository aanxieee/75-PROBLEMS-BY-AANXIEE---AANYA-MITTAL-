# 🏦 EMI Risk Calculator — Ridge Regression

> Loan lene se pehle plan bana lo — EMI afford hogi ya nahi, guess mat karo.

A Streamlit-based EMI risk assessment tool that uses **Ridge Regression** to predict whether a loan EMI is affordable based on your income, expenses, and loan terms.

## 🚀 Live Demo

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://emi-risk-calculator.streamlit.app)

## 📊 What It Does

1. **EMI Risk Check** — Enter income, expenses, loan amount, tenure & interest rate → get EMI amount, Risk Score (0-100), and Debt-to-Income ratio
2. **How It Works** — Ridge Regression explanation + synthetic dataset details

## 🧠 Tech Stack

| Component | Tool |
|:----------|:-----|
| ML Model | Ridge Regression (`sklearn`) |
| Preprocessing | StandardScaler (`sklearn`) |
| Data | Synthetic dataset (500 rows, `numpy` + `pandas`) |
| Frontend | Streamlit |
| Language | Python 3.10+ |

## 📐 How Risk Score Works

```
EMI = P × r × (1+r)^n / ((1+r)^n - 1)
DTI Ratio = (EMI / Monthly Income) × 100
Risk Score = f(income, expenses, loan_amount, tenure, interest_rate) → 0-100
```

| Risk Level | Score | Meaning |
|:-----------|:------|:--------|
| 🟢 Low | 0–32 | EMI is comfortable |
| 🟡 Medium | 33–65 | Manageable, needs planning |
| 🔴 High | 66–100 | May strain finances |

## 🗂️ Project Structure

```
LV1_PROBLEM_11_EMI_RISK_CALCULATOR/
├── app.py                 # Streamlit app
├── src/
│   ├── __init__.py
│   ├── model.py           # Ridge Regression + EMI formula
│   └── preprocessor.py    # StandardScaler + input prep
├── data/
│   └── emi_data.csv       # Synthetic dataset (500 rows)
├── requirements.txt
├── .gitignore
└── README.md
```

## ⚡ Run Locally

```bash
git clone https://github.com/aanxieee/LV1_PROBLEM_11_EMI_RISK_CALCULATOR.git
cd LV1_PROBLEM_11_EMI_RISK_CALCULATOR
pip install -r requirements.txt
streamlit run app.py
```

## ⚠️ Disclaimer

This tool uses a **synthetic dataset** and is built for **educational purposes only**. It is **not financial advice**. Real credit risk assessment involves credit scores, employment history, collateral, and regulated processes. Always consult a certified financial advisor.

---

### Day 11/75 — 75 Hard Engineer Edition 🔥

Built by [Aanya Mittal](https://github.com/aanxieee) | Fintech × AI/ML
