# 💸 PayTrack — UPI Spend Analyzer

> Day 02/75 — 75 Problems. 75 Real-World AI Solutions.

## 🔴 The Problem
Every month end mera wallet empty hota hai.
Pata nahi kahan jaata hai paisa.
PDF statement aata hai — 200 transactions — manually dekhna impossible.

## 💡 The Solution
Upload your UPI transaction PDF.
PayTrack clusters your spending into patterns automatically.
Tells you exactly — **where your money is leaking.**

## 🤖 ML Technique
- **Algorithm:** KMeans Clustering (Unsupervised Learning)
- **Why:** No labels needed — patterns emerge from raw data
- **Libraries:** scikit-learn, pdfplumber, pandas, plotly

## ✨ Features
- PDF upload → auto parse transactions
- Spending clusters — "Foodie Days", "Impulse Buys", "Transport Heavy"
- Top 5 merchants eating your money
- Day-wise and week-wise spend heatmap

## 📂 Structure
```
day-02-paytrack/
├── app.py
├── requirements.txt
├── .gitignore
└── README.md
```

## ⚠️ Data Privacy
Personal transaction data is never pushed to GitHub.
.gitignore handles this automatically.

## 🚀 Run Locally
```bash
pip install -r requirements.txt
streamlit run app.py
```

## 🌐 Live Demo
[Replit Link — coming soon]

## 📚 What I Learned
- Parsing real PDFs with pdfplumber
- KMeans clustering on personal financial data
- Turning raw transactions into human-readable insights

---
*Day 02/75 — #75DayAIChallenge #PayTrack #BuildInPublic*
