"""
app.py — Stock Return Predictor
Day 06/75 | #75problemAIChallenge

Predict stock/index returns using Polynomial Regression.
Built during geopolitical uncertainty — because markets don't wait.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime

from src.data_fetcher import fetch_stock_data, get_stock_info, PRESETS
from src.preprocessor import (
    engineer_features,
    get_feature_columns,
    prepare_future_features,
)
from src.predictor import StockPredictor, calculate_sip_projection


# ── Page config ──
st.set_page_config(
    page_title="Stock Return Predictor",
    page_icon="📈",
    layout="wide",
)

# ── Custom CSS ──
st.markdown("""
<style>
    .stMetric { background: #0e1117; border-radius: 10px; padding: 10px; }
    div[data-testid="stMetricValue"] { font-size: 1.4rem; }
    .disclaimer {
        background: #1a1a2e; padding: 12px 16px; border-radius: 8px;
        border-left: 4px solid #e94560; font-size: 0.85rem; margin-top: 20px;
    }
</style>
""", unsafe_allow_html=True)

# ── Header ──
st.title("📈 Stock Return Predictor")
st.caption(
    "Polynomial Regression on real market data — predict returns in volatile times.  "
    "Day 06/75 • #75problemAIChallenge"
)

# ── Sidebar — Stock Selection ──
with st.sidebar:
    st.header("🔍 Select Stock / Index")

    use_preset = st.toggle("Use quick presets", value=True)

    if use_preset:
        selected_name = st.selectbox("Pick stock/index", list(PRESETS.keys()))
        ticker = PRESETS[selected_name]
    else:
        ticker = st.text_input(
            "Enter ticker symbol",
            value="^NSEI",
            help="Examples: ^NSEI (NIFTY), RELIANCE.NS, TCS.NS, AAPL",
        )

    data_years = st.slider("Historical data (years)", 1, 5, 3)
    poly_degree = st.slider("Polynomial degree", 2, 4, 2,
                            help="Higher = more flexible curve, risk of overfitting")

    fetch_btn = st.button("🚀 Fetch & Predict", type="primary", use_container_width=True)

    st.markdown("---")
    st.markdown(
        '<div class="disclaimer">⚠️ <b>Disclaimer:</b> This is an educational project, '
        "not financial advice. Polynomial regression is a simplified model — "
        "real markets are far more complex. Always consult a financial advisor.</div>",
        unsafe_allow_html=True,
    )

# ── Session state ──
if "stock_data" not in st.session_state:
    st.session_state.stock_data = None
    st.session_state.features_df = None
    st.session_state.model = None
    st.session_state.metrics = None
    st.session_state.ticker = None
    st.session_state.stock_info = None

# ── Fetch & Train on button click ──
if fetch_btn:
    with st.spinner("Fetching market data..."):
        raw_data = fetch_stock_data(ticker, period_years=data_years)

    if raw_data.empty:
        st.error(
            f"❌ No data found for `{ticker}`. Check the ticker symbol and try again."
        )
    else:
        with st.spinner("Engineering features & training model..."):
            info = get_stock_info(ticker)
            features_df = engineer_features(raw_data)

            feature_cols = get_feature_columns()
            X = features_df[feature_cols]
            y = features_df["Close"]

            model = StockPredictor(degree=poly_degree)
            metrics = model.fit(X, y)

        # Save to session state
        st.session_state.stock_data = raw_data
        st.session_state.features_df = features_df
        st.session_state.model = model
        st.session_state.metrics = metrics
        st.session_state.ticker = ticker
        st.session_state.stock_info = info

        st.success(
            f"✅ Loaded {len(raw_data)} days of data for "
            f"**{info.get('name', ticker)}** — model trained!"
        )

# ── Main content (only if data loaded) ──
if st.session_state.stock_data is not None:
    data = st.session_state.stock_data
    features_df = st.session_state.features_df
    model = st.session_state.model
    metrics = st.session_state.metrics
    info = st.session_state.stock_info

    # ── Tabs ──
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Stock Overview",
        "🔮 Prediction",
        "💰 SIP Calculator",
        "📈 Chart",
    ])

    # ════════════════════════════════════════════
    # TAB 1 — Stock Overview
    # ════════════════════════════════════════════
    with tab1:
        st.subheader(f"{info.get('name', st.session_state.ticker)}")

        col1, col2, col3, col4 = st.columns(4)
        latest = data.iloc[-1]
        prev = data.iloc[-2] if len(data) > 1 else latest

        price_change = latest["Close"] - prev["Close"]
        price_change_pct = (price_change / prev["Close"]) * 100

        col1.metric("Current Price",
                     f"₹{latest['Close']:,.2f}",
                     f"{price_change_pct:+.2f}%")
        col2.metric("52W High",
                     f"₹{info['52w_high']:,.2f}" if info.get("52w_high") else "N/A")
        col3.metric("52W Low",
                     f"₹{info['52w_low']:,.2f}" if info.get("52w_low") else "N/A")
        col4.metric("Data Points", f"{len(data)} days")

        st.markdown("---")

        st.markdown("**Model Training Metrics**")
        mc1, mc2, mc3, mc4 = st.columns(4)
        mc1.metric("Train R²", f"{metrics['train_r2']}")
        mc2.metric("Test R²", f"{metrics['test_r2']}")
        mc3.metric("Test MAE", f"₹{metrics['test_mae']}")
        mc4.metric("Poly Degree", f"{metrics['degree']}")

        st.caption(
            f"Trained on {metrics['n_train']} days, tested on {metrics['n_test']} days "
            f"(80/20 time-based split)"
        )

        st.markdown("---")

        st.markdown("**Recent Data (last 10 days)**")
        recent = data.tail(10)[["Date", "Open", "High", "Low", "Close", "Volume"]].copy()
        recent["Date"] = recent["Date"].dt.strftime("%d %b %Y")
        recent["Volume"] = recent["Volume"].apply(lambda x: f"{x:,.0f}")
        for c in ["Open", "High", "Low", "Close"]:
            recent[c] = recent[c].apply(lambda x: f"₹{x:,.2f}")
        st.dataframe(recent, use_container_width=True, hide_index=True)

    # ════════════════════════════════════════════
    # TAB 2 — Prediction
    # ════════════════════════════════════════════
    with tab2:
        st.subheader("🔮 Return Prediction")

        pcol1, pcol2 = st.columns(2)
        with pcol1:
            pred_mode = st.radio(
                "Prediction window",
                ["7 Days", "30 Days", "Custom"],
                horizontal=True,
            )
        with pcol2:
            if pred_mode == "Custom":
                pred_days = st.number_input("Days ahead", 1, 180, 15)
            elif pred_mode == "7 Days":
                pred_days = 7
            else:
                pred_days = 30

        confidence_level = st.select_slider(
            "Confidence interval",
            options=[0.90, 0.95, 0.99],
            value=0.95,
            format_func=lambda x: f"{int(x*100)}%",
        )

        if st.button("🔮 Predict", type="primary"):
            with st.spinner("Running predictions..."):
                feature_cols = get_feature_columns()

                # Future feature rows
                future_X = prepare_future_features(features_df, pred_days)
                result = model.predict(future_X[feature_cols],
                                       confidence=confidence_level)

                current_price = features_df["Close"].iloc[-1]
                returns = model.predict_returns(current_price,
                                                result["predicted"])

            # Display
            st.markdown("---")
            rc1, rc2, rc3 = st.columns(3)
            rc1.metric("Current Price", f"₹{returns['current_price']:,.2f}")
            rc2.metric(
                f"Predicted ({pred_days}d)",
                f"₹{returns['predicted_price']:,.2f}",
                f"{returns['return_pct']:+.2f}%",
            )
            rc3.metric("Signal", returns["direction"])

            st.info(
                f"**Confidence band:** ₹{result['lower'][-1]:,.2f} — "
                f"₹{result['upper'][-1]:,.2f}  "
                f"({int(confidence_level*100)}% CI)"
            )

            # Mini prediction chart
            fig = go.Figure()
            dates_range = pd.date_range(
                start=data["Date"].iloc[-1],
                periods=pred_days + 1,
                freq="B",
            )[1:]

            fig.add_trace(go.Scatter(
                x=dates_range, y=result["upper"],
                mode="lines", line=dict(width=0),
                showlegend=False,
            ))
            fig.add_trace(go.Scatter(
                x=dates_range, y=result["lower"],
                mode="lines", line=dict(width=0),
                fill="tonexty",
                fillcolor="rgba(99, 110, 250, 0.2)",
                name=f"{int(confidence_level*100)}% CI",
            ))
            fig.add_trace(go.Scatter(
                x=dates_range, y=result["predicted"],
                mode="lines+markers",
                name="Predicted Price",
                line=dict(color="#636EFA", width=2),
            ))
            fig.add_hline(
                y=current_price,
                line_dash="dash",
                line_color="gray",
                annotation_text=f"Current: ₹{current_price:,.2f}",
            )

            fig.update_layout(
                title=f"{pred_days}-Day Price Prediction",
                xaxis_title="Date",
                yaxis_title="Price (₹)",
                template="plotly_dark",
                height=400,
            )
            st.plotly_chart(fig, use_container_width=True)

            # Store predicted annual return for SIP tab
            daily_return = returns["return_pct"] / pred_days
            st.session_state.predicted_annual_return = daily_return * 252

    # ════════════════════════════════════════════
    # TAB 3 — SIP Calculator
    # ════════════════════════════════════════════
    with tab3:
        st.subheader("💰 SIP Return Projection")

        if "predicted_annual_return" not in st.session_state:
            st.warning("⬅️ Run a prediction first (Tab 2) to get the projected return rate.")
            projected_return = 12.0
        else:
            projected_return = st.session_state.predicted_annual_return

        sc1, sc2, sc3 = st.columns(3)
        with sc1:
            sip_amount = st.number_input("Monthly SIP (₹)", 500, 1_000_000, 5000,
                                         step=500)
        with sc2:
            sip_months = st.number_input("Duration (months)", 1, 360, 36)
        with sc3:
            annual_return = st.number_input(
                "Expected annual return (%)",
                value=round(float(projected_return), 2),
                step=0.5,
                help="Pre-filled from prediction. Edit to compare scenarios.",
            )

        if st.button("📊 Calculate SIP", type="primary"):
            sip = calculate_sip_projection(sip_amount, sip_months, annual_return)

            st.markdown("---")
            sc1, sc2, sc3 = st.columns(3)
            sc1.metric("Total Invested", f"₹{sip['total_invested']:,.0f}")
            sc2.metric("Projected Value", f"₹{sip['future_value']:,.0f}")
            sc3.metric("Expected Gains",
                       f"₹{sip['gains']:,.0f}",
                       f"{sip['gain_pct']:+.1f}%")

            # SIP growth chart
            bd = pd.DataFrame(sip["breakdown"])
            fig_sip = go.Figure()

            fig_sip.add_trace(go.Scatter(
                x=bd["month"], y=bd["invested"],
                name="Amount Invested",
                fill="tozeroy",
                line=dict(color="#FF6B6B"),
            ))
            fig_sip.add_trace(go.Scatter(
                x=bd["month"], y=bd["value"],
                name="Portfolio Value",
                fill="tonexty",
                line=dict(color="#4ECDC4"),
            ))

            fig_sip.update_layout(
                title="SIP Growth Over Time",
                xaxis_title="Month",
                yaxis_title="Amount (₹)",
                template="plotly_dark",
                height=400,
            )
            st.plotly_chart(fig_sip, use_container_width=True)

    # ════════════════════════════════════════════
    # TAB 4 — Chart (Actual vs Predicted)
    # ════════════════════════════════════════════
    with tab4:
        st.subheader("📈 Actual vs Predicted — Full History")

        feature_cols = get_feature_columns()
        X_all = features_df[feature_cols]
        result_all = model.predict(X_all, confidence=0.95)
        split_idx = metrics["split_idx"]

        fig_full = go.Figure()

        # Confidence band
        fig_full.add_trace(go.Scatter(
            x=features_df["Date"], y=result_all["upper"],
            mode="lines", line=dict(width=0),
            showlegend=False,
        ))
        fig_full.add_trace(go.Scatter(
            x=features_df["Date"], y=result_all["lower"],
            mode="lines", line=dict(width=0),
            fill="tonexty",
            fillcolor="rgba(99, 110, 250, 0.15)",
            name="95% CI",
        ))

        # Actual
        fig_full.add_trace(go.Scatter(
            x=features_df["Date"], y=features_df["Close"],
            name="Actual Price",
            line=dict(color="#FF6B6B", width=1.5),
        ))

        # Predicted
        fig_full.add_trace(go.Scatter(
            x=features_df["Date"], y=result_all["predicted"],
            name="Predicted Price",
            line=dict(color="#636EFA", width=2),
        ))

        # Train/Test split line
        split_date = features_df["Date"].iloc[split_idx]
        fig_full.add_vline(
            x=split_date,
            line_dash="dot",
            line_color="yellow",
            annotation_text="← Train | Test →",
            annotation_font_color="yellow",
        )

        fig_full.update_layout(
            title="Model Fit: Actual vs Predicted Closing Price",
            xaxis_title="Date",
            yaxis_title="Price (₹)",
            template="plotly_dark",
            height=500,
            legend=dict(orientation="h", yanchor="bottom", y=1.02),
        )
        st.plotly_chart(fig_full, use_container_width=True)

        # Residuals chart
        residuals = features_df["Close"] - result_all["predicted"]

        fig_res = go.Figure()
        fig_res.add_trace(go.Bar(
            x=features_df["Date"], y=residuals,
            marker_color=np.where(residuals >= 0, "#4ECDC4", "#FF6B6B"),
            name="Residual",
        ))
        fig_res.add_hline(y=0, line_dash="dash", line_color="gray")
        fig_res.add_vline(
            x=split_date,
            line_dash="dot",
            line_color="yellow",
        )
        fig_res.update_layout(
            title="Prediction Residuals (Actual - Predicted)",
            xaxis_title="Date",
            yaxis_title="Residual (₹)",
            template="plotly_dark",
            height=300,
        )
        st.plotly_chart(fig_res, use_container_width=True)

else:
    # ── Landing state ──
    st.info("👈 Select a stock/index from the sidebar and click **Fetch & Predict** to begin.")

    st.markdown("""
    ### How it works
    1. **Fetch** real historical data via Yahoo Finance
    2. **Engineer** lagged features — rolling averages, momentum, volatility, RSI
    3. **Train** a Polynomial Regression model (80/20 time-based split)
    4. **Predict** future returns with confidence intervals
    5. **Project** SIP returns based on predicted growth rate

    > Built during a time when geopolitical tensions are shaking markets.
    > If you've already invested — know where your money might be heading.
    """)

# ── Footer ──
st.markdown("---")
st.markdown(
    "<center>Built with ❤️ by <b>Aanya</b> • "
    '<a href="https://github.com/aanxieee">GitHub</a> • '
    "Day 06/75 • #75problemAIChallenge</center>",
    unsafe_allow_html=True,
)
