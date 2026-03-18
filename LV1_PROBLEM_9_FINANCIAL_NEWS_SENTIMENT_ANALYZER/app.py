"""
Day 09/75 — Financial News Sentiment Analyzer
VADER Sentiment Analysis + Custom Financial Lexicon
Built by: aanxieee | 75-Day AI Challenge
"""

import streamlit as st
import pandas as pd
import io
from datetime import datetime

from src.sentiment_analyzer import (
    analyze_headline,
    analyze_bulk,
    get_market_mood,
    SentimentResult,
    FINANCIAL_LEXICON,
)
from src.visualizer import (
    confidence_gauge,
    score_breakdown_bar,
    bulk_sentiment_chart,
    sentiment_pie,
    sentiment_trend,
)


# ── Page Config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Financial Sentiment Analyzer",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    .stApp {
        font-family: 'Inter', sans-serif;
    }

    .main-header {
        text-align: center;
        padding: 1rem 0 0.5rem;
    }
    .main-header h1 {
        font-size: 2rem;
        font-weight: 700;
        background: linear-gradient(135deg, #448AFF, #00C853);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.25rem;
    }
    .main-header p {
        color: #888; font-size: 0.95rem;
    }

    .signal-card {
        border-radius: 12px;
        padding: 1.25rem;
        text-align: center;
        border: 1px solid #333;
    }
    .signal-card h2 { margin: 0; font-size: 1.8rem; }
    .signal-card p { margin: 0.25rem 0 0; font-size: 0.85rem; color: #aaa; }

    .buy-card { background: linear-gradient(135deg, #00C85320, #00C85308); border-color: #00C853; }
    .sell-card { background: linear-gradient(135deg, #FF174420, #FF174408); border-color: #FF1744; }
    .hold-card { background: linear-gradient(135deg, #FFC10720, #FFC10708); border-color: #FFC107; }

    .mood-banner {
        text-align: center;
        padding: 1rem;
        border-radius: 12px;
        border: 1px solid #333;
        margin: 0.5rem 0;
    }

    .matched-term {
        display: inline-block;
        background: #1a1a2e;
        border: 1px solid #448AFF;
        border-radius: 20px;
        padding: 2px 10px;
        margin: 2px;
        font-size: 0.8rem;
        color: #448AFF;
    }

    .disclaimer {
        text-align: center;
        color: #666;
        font-size: 0.75rem;
        padding: 1rem 0;
        border-top: 1px solid #222;
        margin-top: 2rem;
    }

    div[data-testid="stMetric"] {
        background: #111;
        border: 1px solid #333;
        border-radius: 8px;
        padding: 0.75rem;
    }
</style>
""", unsafe_allow_html=True)


# ── Session State ────────────────────────────────────────────────────────────
if "history" not in st.session_state:
    st.session_state.history = []


def add_to_history(result: SentimentResult):
    """Append result to session history for trend tracking."""
    st.session_state.history.append({
        "index": len(st.session_state.history) + 1,
        "headline": result.headline,
        "compound": result.compound,
        "label": result.label,
        "signal": result.signal,
        "confidence": result.confidence,
        "timestamp": datetime.now().strftime("%H:%M:%S"),
    })


def render_signal_card(result: SentimentResult):
    """Render the colored signal card."""
    card_class = (
        "buy-card" if result.signal == "BUY"
        else "sell-card" if result.signal == "SELL"
        else "hold-card"
    )
    emoji = "🟢" if result.signal == "BUY" else "🔴" if result.signal == "SELL" else "🟡"

    st.markdown(f"""
    <div class="signal-card {card_class}">
        <h2>{emoji} {result.signal}</h2>
        <p>Compound: {result.compound:+.4f} | Confidence: {result.confidence}%</p>
    </div>
    """, unsafe_allow_html=True)


# ── Header ───────────────────────────────────────────────────────────────────
st.markdown("""
<div class="main-header">
    <h1>📊 Financial News Sentiment Analyzer</h1>
    <p>VADER + Custom Financial Lexicon · Paste headlines → Get market signals</p>
</div>
""", unsafe_allow_html=True)


# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ Settings")

    mode = st.radio(
        "Analysis Mode",
        ["📝 Single Headline", "📋 Bulk Headlines", "📄 CSV Upload"],
        index=0,
    )

    st.markdown("---")

    # Session stats
    if st.session_state.history:
        st.markdown("### 📈 Session Stats")
        h = st.session_state.history
        st.metric("Total Analyzed", len(h))

        pos_c = sum(1 for x in h if x["label"] == "Positive")
        neg_c = sum(1 for x in h if x["label"] == "Negative")
        st.metric("Bullish / Bearish", f"{pos_c} / {neg_c}")

        avg = sum(x["compound"] for x in h) / len(h)
        st.metric("Avg Compound", f"{avg:+.4f}")

    st.markdown("---")

    if st.button("🗑️ Clear History", use_container_width=True):
        st.session_state.history = []
        st.rerun()

    st.markdown("---")
    with st.expander("📖 Financial Lexicon"):
        st.caption("Custom terms added to VADER for finance context:")
        bullish = {k: v for k, v in FINANCIAL_LEXICON.items() if v > 0}
        bearish = {k: v for k, v in FINANCIAL_LEXICON.items() if v < 0}
        st.markdown(f"**Bullish terms:** {len(bullish)}")
        st.markdown(f"**Bearish terms:** {len(bearish)}")
        st.dataframe(
            pd.DataFrame(
                [(k, v) for k, v in sorted(FINANCIAL_LEXICON.items(), key=lambda x: -x[1])],
                columns=["Term", "Score"],
            ),
            hide_index=True,
            height=250,
        )


# ── Main Content ─────────────────────────────────────────────────────────────

# ═══════════════════════════════════════════════════════════════════
# MODE 1: Single Headline
# ═══════════════════════════════════════════════════════════════════
if mode == "📝 Single Headline":
    st.markdown("### 📝 Analyze a Headline")

    headline = st.text_input(
        "Paste a financial news headline:",
        placeholder="e.g. RBI cuts repo rate by 25 bps; Sensex rallies 500 points",
    )

    col_btn, col_sample = st.columns([1, 2])
    with col_btn:
        analyze_btn = st.button("🔍 Analyze", type="primary", use_container_width=True)
    with col_sample:
        samples = [
            "RBI cuts repo rate by 25 bps to boost growth",
            "Sensex crashes 1000 points on FII selling spree",
            "Infosys beats Q3 estimates, revenue up 12% YoY",
            "Global recession fears drag Indian markets lower",
            "Reliance announces massive share buyback program",
        ]
        sample = st.selectbox("Or try a sample:", [""] + samples, label_visibility="collapsed")
        if sample and not headline:
            headline = sample

    if (analyze_btn or sample) and headline:
        result = analyze_headline(headline)
        add_to_history(result)

        # Signal card
        render_signal_card(result)

        st.markdown("")

        # Gauge + Breakdown side by side
        col1, col2 = st.columns(2)
        with col1:
            st.plotly_chart(confidence_gauge(result), use_container_width=True)
        with col2:
            st.plotly_chart(score_breakdown_bar(result), use_container_width=True)

        # Matched financial terms
        if result.matched_terms:
            st.markdown("**🏷️ Matched Financial Terms:**")
            terms_html = " ".join(
                f'<span class="matched-term">{t}</span>' for t in result.matched_terms
            )
            st.markdown(terms_html, unsafe_allow_html=True)

        # Detailed scores
        with st.expander("📊 Detailed Scores"):
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Compound", f"{result.compound:+.4f}")
            c2.metric("Positive", f"{result.positive:.4f}")
            c3.metric("Negative", f"{result.negative:.4f}")
            c4.metric("Neutral", f"{result.neutral:.4f}")


# ═══════════════════════════════════════════════════════════════════
# MODE 2: Bulk Headlines
# ═══════════════════════════════════════════════════════════════════
elif mode == "📋 Bulk Headlines":
    st.markdown("### 📋 Bulk Headline Analysis")
    st.caption("Paste multiple headlines — one per line.")

    text_block = st.text_area(
        "Headlines:",
        height=200,
        placeholder="RBI cuts repo rate by 25 bps\nSensex crashes 1000 points\nInfosys beats estimates...",
    )

    if st.button("🔍 Analyze All", type="primary", use_container_width=True):
        if text_block.strip():
            headlines = [h.strip() for h in text_block.strip().split("\n") if h.strip()]
            results = analyze_bulk(headlines)

            # Add all to history
            for r in results:
                add_to_history(r)

            # Market mood
            mood = get_market_mood(results)
            mood_color = (
                "#00C853" if "Bullish" in mood["mood"]
                else "#FF1744" if "Bearish" in mood["mood"]
                else "#FFC107"
            )
            st.markdown(f"""
            <div class="mood-banner" style="border-color: {mood_color};">
                <h2 style="margin:0;">{mood['mood']}</h2>
                <p style="color:#aaa; margin:0.25rem 0 0;">
                    Avg Compound: {mood['avg_compound']:+.4f} ·
                    Signal: <strong>{mood['signal']}</strong> ·
                    {mood['total']} headlines analyzed
                </p>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("")

            # Charts
            col1, col2 = st.columns([3, 2])
            with col1:
                st.plotly_chart(bulk_sentiment_chart(results), use_container_width=True)
            with col2:
                st.plotly_chart(sentiment_pie(results), use_container_width=True)

            # Results table
            st.markdown("#### 📊 Detailed Results")
            df = pd.DataFrame([
                {
                    "#": i + 1,
                    "Headline": r.headline[:60] + ("..." if len(r.headline) > 60 else ""),
                    "Compound": f"{r.compound:+.4f}",
                    "Label": r.label,
                    "Signal": r.signal,
                    "Confidence": f"{r.confidence}%",
                }
                for i, r in enumerate(results)
            ])
            st.dataframe(df, hide_index=True, use_container_width=True)

            # CSV download
            full_df = pd.DataFrame([
                {
                    "headline": r.headline,
                    "compound": r.compound,
                    "positive": r.positive,
                    "negative": r.negative,
                    "neutral": r.neutral,
                    "label": r.label,
                    "signal": r.signal,
                    "confidence": r.confidence,
                    "matched_terms": ", ".join(r.matched_terms),
                }
                for r in results
            ])
            csv_data = full_df.to_csv(index=False)
            st.download_button(
                "📥 Download Results CSV",
                data=csv_data,
                file_name="sentiment_results.csv",
                mime="text/csv",
                use_container_width=True,
            )
        else:
            st.warning("Please paste at least one headline.")


# ═══════════════════════════════════════════════════════════════════
# MODE 3: CSV Upload
# ═══════════════════════════════════════════════════════════════════
elif mode == "📄 CSV Upload":
    st.markdown("### 📄 CSV Upload Analysis")
    st.caption("Upload a CSV file with a column named **headline** or **text** or **title**.")

    uploaded = st.file_uploader("Upload CSV", type=["csv"])

    if uploaded:
        try:
            df_input = pd.read_csv(uploaded)
            st.markdown(f"**Loaded:** {len(df_input)} rows, columns: {', '.join(df_input.columns)}")

            # Find the text column
            text_col = None
            for col_name in ["headline", "Headline", "text", "Text", "title", "Title",
                             "news", "News", "content", "Content"]:
                if col_name in df_input.columns:
                    text_col = col_name
                    break

            if text_col is None:
                st.error("Could not find a text column. Please use 'headline', 'text', or 'title' as column name.")
            else:
                st.success(f"Using column: **{text_col}**")

                if st.button("🔍 Analyze CSV", type="primary", use_container_width=True):
                    headlines = df_input[text_col].dropna().astype(str).tolist()
                    results = analyze_bulk(headlines)

                    for r in results:
                        add_to_history(r)

                    # Market mood
                    mood = get_market_mood(results)
                    mood_color = (
                        "#00C853" if "Bullish" in mood["mood"]
                        else "#FF1744" if "Bearish" in mood["mood"]
                        else "#FFC107"
                    )
                    st.markdown(f"""
                    <div class="mood-banner" style="border-color: {mood_color};">
                        <h2 style="margin:0;">{mood['mood']}</h2>
                        <p style="color:#aaa; margin:0.25rem 0 0;">
                            Avg Compound: {mood['avg_compound']:+.4f} ·
                            Signal: <strong>{mood['signal']}</strong> ·
                            {mood['total']} headlines analyzed
                        </p>
                    </div>
                    """, unsafe_allow_html=True)

                    col1, col2 = st.columns([3, 2])
                    with col1:
                        st.plotly_chart(bulk_sentiment_chart(results), use_container_width=True)
                    with col2:
                        st.plotly_chart(sentiment_pie(results), use_container_width=True)

                    # Results table
                    st.markdown("#### 📊 Detailed Results")
                    out_df = pd.DataFrame([
                        {
                            "#": i + 1,
                            "Headline": r.headline[:60] + ("..." if len(r.headline) > 60 else ""),
                            "Compound": f"{r.compound:+.4f}",
                            "Label": r.label,
                            "Signal": r.signal,
                            "Confidence": f"{r.confidence}%",
                        }
                        for i, r in enumerate(results)
                    ])
                    st.dataframe(out_df, hide_index=True, use_container_width=True)

                    # Download enriched CSV
                    enriched = df_input.copy()
                    enriched["compound"] = [r.compound for r in results] + [None] * (len(enriched) - len(results))
                    enriched["sentiment_label"] = [r.label for r in results] + [None] * (len(enriched) - len(results))
                    enriched["signal"] = [r.signal for r in results] + [None] * (len(enriched) - len(results))
                    enriched["confidence"] = [r.confidence for r in results] + [None] * (len(enriched) - len(results))

                    csv_out = enriched.to_csv(index=False)
                    st.download_button(
                        "📥 Download Enriched CSV",
                        data=csv_out,
                        file_name="enriched_sentiment.csv",
                        mime="text/csv",
                        use_container_width=True,
                    )

        except Exception as e:
            st.error(f"Error reading CSV: {e}")


# ═══════════════════════════════════════════════════════════════════
# Sentiment Trend (always visible if history exists)
# ═══════════════════════════════════════════════════════════════════
if st.session_state.history:
    st.markdown("---")
    st.markdown("### 📈 Session Sentiment Trend")
    st.plotly_chart(sentiment_trend(st.session_state.history), use_container_width=True)

    with st.expander("📋 Full Session History"):
        hist_df = pd.DataFrame(st.session_state.history)
        hist_df = hist_df[["index", "timestamp", "headline", "compound", "label", "signal", "confidence"]]
        st.dataframe(hist_df, hide_index=True, use_container_width=True)


# ── Disclaimer ───────────────────────────────────────────────────────────────
st.markdown("""
<div class="disclaimer">
    ⚠️ <strong>Disclaimer:</strong> This tool is for educational purposes only. Not financial advice.
    Sentiment analysis is one of many factors in market analysis. Always do your own research (DYOR).
    <br><br>
    Day 09/75 — 75 Hard Engineer Edition · Built by
    <a href="https://github.com/aanxieee" target="_blank">aanxieee</a>
</div>
""", unsafe_allow_html=True)
