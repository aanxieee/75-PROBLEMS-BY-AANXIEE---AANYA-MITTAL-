# 📊 Financial News Sentiment Analyzer

**Day 09/75 — 75 Hard Engineer Edition**
VADER Sentiment Analysis + Custom Financial Lexicon for market signal generation.

## What It Does

Paste any financial news headline → get an instant sentiment score, market signal (BUY/SELL/HOLD), and confidence meter. Understands Indian financial context (RBI, Sensex, FII flows).

## Features

- **Single Headline Analysis** — paste one headline, get VADER score + gauge + signal
- **Bulk Analysis** — paste multiple headlines, get aggregate market mood + charts
- **CSV Upload** — upload a CSV with headlines, download enriched results
- **Market Mood** — aggregate sentiment into overall bullish/bearish signal
- **Confidence Meter** — visual gauge showing signal strength (0-100%)
- **Sentiment Trend** — session-based tracking of all analyzed headlines
- **Custom Financial Lexicon** — 60+ finance terms (rate cut, FII selling, buyback, etc.) added to VADER for accurate market context
- **Export** — download results as CSV

## Custom Financial Lexicon

VADER misreads financial context. Example: "RBI **cuts** rate" — VADER sees "cuts" as negative, but it's bullish for markets.

We inject 60+ custom terms:
| Bullish | Bearish |
|---------|---------|
| rate cut, rally, buyback, FII inflow, beat estimates | crash, selloff, FII selling, recession, downgrade |

## Tech Stack

- **vaderSentiment** — NLP sentiment scoring
- **Streamlit** — interactive web UI
- **Plotly** — gauge, bar, pie, and trend charts
- **Pandas** — data handling + CSV I/O

## Setup

```bash
git clone https://github.com/aanxieee/day-09-financial-news-sentiment.git
cd day-09-financial-news-sentiment
pip install -r requirements.txt
streamlit run app.py
```

## Folder Structure

```
day-09-financial-news-sentiment/
├── app.py                        # Streamlit UI
├── src/
│   ├── sentiment_analyzer.py     # VADER + financial lexicon
│   └── visualizer.py             # Plotly charts
├── requirements.txt
├── .gitignore
└── README.md
```

## Disclaimer

⚠️ This tool is for **educational purposes only**. Not financial advice. Always DYOR.

---

**Day 09/75** · 75 Hard — Engineer Edition · Built by [aanxieee](https://github.com/aanxieee)
