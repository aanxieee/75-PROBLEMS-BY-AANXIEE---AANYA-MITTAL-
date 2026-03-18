# 📈 Stock Return Predictor — Polynomial Regression

### When wars move markets, where is your money heading?

---

## Why I Built This

I invest through SIPs — NIFTY, index funds, the usual.

Then geopolitical tensions hit. India-Pakistan escalation. Global conflicts making headlines every other day. And suddenly my portfolio was a rollercoaster I didn't sign up for.

I had one question: **If I've already invested, where are my returns heading?**

So I built a predictor. Not a crystal ball — a data-driven, polynomial regression model trained on real historical market data. Because in volatile times, even an imperfect estimate beats blind hope.

---

## What It Does

| Feature | Description |
|---------|-------------|
| **🔍 Search Any Stock** | Type any ticker (NIFTY 50, Reliance, TCS, or any global stock) |
| **🔮 Predict Returns** | 7-day, 30-day, or custom period return prediction with confidence intervals |
| **💰 SIP Calculator** | Input your monthly SIP amount → see projected corpus using model's predicted return |
| **📈 Actual vs Predicted** | Full history chart with confidence band + residual analysis |

---

## How It Works

1. **Fetch** real historical data via Yahoo Finance (`yfinance`)
2. **Engineer features** — SMA (5/20/50), price momentum, volatility, RSI-14, volume ratio
3. **Train** Polynomial Regression (`PolynomialFeatures` + `LinearRegression`)
4. **Predict** future closing prices with confidence intervals
5. **Project** SIP returns based on model's predicted growth rate

---

## Tech Stack

- **Data:** yfinance
- **ML:** scikit-learn (PolynomialFeatures, LinearRegression, StandardScaler)
- **Frontend:** Streamlit
- **Charts:** Plotly
- **Core:** pandas, numpy

---

## Run Locally

```bash
git clone https://github.com/aanxieee/75-problems-ai-challenge.git
cd day-06-stock-return-predictor
pip install -r requirements.txt
streamlit run app.py
```

---

## Project Structure

```
day-06-stock-return-predictor/
├── app.py                  # Streamlit app (4 tabs)
├── src/
│   ├── data_fetcher.py     # yfinance data fetching
│   ├── preprocessor.py     # Feature engineering
│   └── predictor.py        # Polynomial regression + SIP calculator
├── requirements.txt
├── .gitignore
└── README.md
```

---

## ⚠️ Disclaimer

This is an **educational project**, not financial advice. Polynomial regression is a simplified model — real markets are influenced by geopolitics, sentiment, policy, and a thousand things no model captures fully. Always consult a qualified financial advisor before making investment decisions.

---

## Day 06/75 • #75problemAIChallenge

**75 Problems. 75 Real-World AI Solutions.**

Built by [Aanya](https://github.com/aanxieee) • [Instagram: @aanxiee](https://instagram.com/aanxiee) • [Website: aanxiee.com](https://aanxiee.com)
