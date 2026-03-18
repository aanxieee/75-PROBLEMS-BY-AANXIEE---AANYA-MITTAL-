"""
Financial News Sentiment Analyzer
VADER + Custom Financial Lexicon for accurate market sentiment scoring.
"""

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from dataclasses import dataclass


# Custom financial terms that VADER misreads
# Positive values = bullish, Negative values = bearish
FINANCIAL_LEXICON = {
    # Bullish terms VADER might miss or misread
    "rate cut": 2.0,
    "rate cuts": 2.0,
    "interest rate cut": 2.5,
    "repo rate cut": 2.5,
    "bull run": 3.0,
    "bullish": 2.5,
    "upgrade": 2.0,
    "upgraded": 2.0,
    "outperform": 2.5,
    "beat estimates": 2.5,
    "beats estimates": 2.5,
    "record high": 3.0,
    "all-time high": 3.0,
    "ath": 2.5,
    "rally": 2.5,
    "rallies": 2.5,
    "rallied": 2.5,
    "surge": 2.5,
    "surges": 2.5,
    "breakout": 2.0,
    "dividend": 1.5,
    "buyback": 2.0,
    "share buyback": 2.0,
    "fii inflow": 2.0,
    "fii buying": 2.0,
    "nifty gains": 2.0,
    "sensex gains": 2.0,
    "green": 1.5,
    "recovery": 2.0,
    "rebounds": 2.0,
    "rebound": 2.0,
    "expansion": 1.5,
    "gdp growth": 2.0,
    "profit jumps": 2.5,
    "strong earnings": 2.5,
    "revenue growth": 2.0,
    "overweight": 1.5,
    "accumulate": 1.5,
    "easing": 1.5,
    "monetary easing": 2.0,
    "stimulus": 2.0,
    "reform": 1.5,
    "reforms": 1.5,

    # Bearish terms VADER might miss
    "rate hike": -2.0,
    "rate hikes": -2.0,
    "interest rate hike": -2.5,
    "bearish": -2.5,
    "downgrade": -2.5,
    "downgraded": -2.5,
    "underperform": -2.0,
    "miss estimates": -2.5,
    "misses estimates": -2.5,
    "correction": -2.0,
    "crash": -3.0,
    "crashes": -3.0,
    "meltdown": -3.0,
    "sell-off": -2.5,
    "selloff": -2.5,
    "bloodbath": -3.0,
    "capitulation": -3.0,
    "fii outflow": -2.0,
    "fii selling": -2.0,
    "nifty falls": -2.0,
    "sensex falls": -2.0,
    "red": -1.5,
    "default": -2.5,
    "bankruptcy": -3.0,
    "recession": -2.5,
    "inflation rises": -2.0,
    "inflation surges": -2.5,
    "slowdown": -2.0,
    "contraction": -2.0,
    "profit warning": -2.5,
    "weak earnings": -2.5,
    "revenue decline": -2.0,
    "underweight": -1.5,
    "tightening": -1.5,
    "monetary tightening": -2.0,
    "hawkish": -1.5,
    "dovish": 1.5,
    "tariff": -1.5,
    "tariffs": -1.5,
    "sanctions": -2.0,
    "scam": -3.0,
    "fraud": -3.0,
}


@dataclass
class SentimentResult:
    """Structured result from sentiment analysis."""
    headline: str
    compound: float
    positive: float
    negative: float
    neutral: float
    label: str       # Positive / Negative / Neutral
    signal: str      # BUY / SELL / HOLD
    confidence: float  # 0-100%
    matched_terms: list


def _build_analyzer() -> SentimentIntensityAnalyzer:
    """Build VADER analyzer with custom financial lexicon injected."""
    analyzer = SentimentIntensityAnalyzer()
    analyzer.lexicon.update(FINANCIAL_LEXICON)
    return analyzer


_analyzer = _build_analyzer()


def analyze_headline(headline: str) -> SentimentResult:
    """Analyze a single headline and return structured result."""
    text = headline.strip()
    if not text:
        return SentimentResult(
            headline=text,
            compound=0.0, positive=0.0, negative=0.0, neutral=1.0,
            label="Neutral", signal="HOLD", confidence=0.0,
            matched_terms=[],
        )

    scores = _analyzer.polarity_scores(text)
    compound = scores["compound"]

    # Determine label
    if compound >= 0.05:
        label = "Positive"
    elif compound <= -0.05:
        label = "Negative"
    else:
        label = "Neutral"

    # Market signal with thresholds
    if compound >= 0.25:
        signal = "BUY"
    elif compound >= 0.05:
        signal = "BUY"
    elif compound <= -0.25:
        signal = "SELL"
    elif compound <= -0.05:
        signal = "SELL"
    else:
        signal = "HOLD"

    # Confidence: absolute compound scaled to 0-100
    confidence = min(abs(compound) * 100, 100.0)

    # Find matched financial terms
    lower_text = text.lower()
    matched = [term for term in FINANCIAL_LEXICON if term in lower_text]

    return SentimentResult(
        headline=text,
        compound=round(compound, 4),
        positive=round(scores["pos"], 4),
        negative=round(scores["neg"], 4),
        neutral=round(scores["neu"], 4),
        label=label,
        signal=signal,
        confidence=round(confidence, 1),
        matched_terms=matched,
    )


def analyze_bulk(headlines: list[str]) -> list[SentimentResult]:
    """Analyze multiple headlines."""
    return [analyze_headline(h) for h in headlines if h.strip()]


def get_market_mood(results: list[SentimentResult]) -> dict:
    """Aggregate sentiment results into overall market mood."""
    if not results:
        return {
            "mood": "No Data",
            "avg_compound": 0.0,
            "positive_pct": 0.0,
            "negative_pct": 0.0,
            "neutral_pct": 0.0,
            "signal": "HOLD",
            "total": 0,
        }

    total = len(results)
    avg_compound = sum(r.compound for r in results) / total
    pos_count = sum(1 for r in results if r.label == "Positive")
    neg_count = sum(1 for r in results if r.label == "Negative")
    neu_count = sum(1 for r in results if r.label == "Neutral")

    if avg_compound >= 0.15:
        mood = "🟢 Bullish"
        signal = "BUY"
    elif avg_compound >= 0.05:
        mood = "🟡 Mildly Bullish"
        signal = "BUY"
    elif avg_compound <= -0.15:
        mood = "🔴 Bearish"
        signal = "SELL"
    elif avg_compound <= -0.05:
        mood = "🟠 Mildly Bearish"
        signal = "SELL"
    else:
        mood = "⚪ Neutral"
        signal = "HOLD"

    return {
        "mood": mood,
        "avg_compound": round(avg_compound, 4),
        "positive_pct": round(pos_count / total * 100, 1),
        "negative_pct": round(neg_count / total * 100, 1),
        "neutral_pct": round(neu_count / total * 100, 1),
        "signal": signal,
        "total": total,
    }
