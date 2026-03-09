"""
app.py — PayTrack
Day 02 / 75-Day AI Challenge
Technique: KMeans Clustering (Unsupervised Learning)
Supports: PhonePe PDF · Paytm PDF · Sample CSV
"""

import os
import tempfile
import pandas as pd
import plotly.express as px
import streamlit as st

from cluster import (
    parse_upi_pdf,
    load_csv,
    run_clustering,
    get_spending_personality,
    get_top_merchants,
)

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="PayTrack",
    page_icon="💸",
    layout="centered",
)

st.title("💸 PayTrack")
st.caption("Day 02 / 75 · Unsupervised Learning · KMeans Clustering")
st.divider()


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("📂 Upload Your Data")

    upload_type = st.radio(
        "Choose input",
        ["PhonePe PDF", "Paytm PDF", "Sample CSV (Demo)"],
        index=2,
    )

    uploaded_file = None
    if upload_type in ("PhonePe PDF", "Paytm PDF"):
        label = "Upload PhonePe PDF" if "PhonePe" in upload_type else "Upload Paytm PDF"
        uploaded_file = st.file_uploader(label, type=["pdf"])
        st.info(
            "Your PDF is processed **in-memory only** — never saved anywhere.",
            icon="🔒"
        )
        st.markdown(
            "**How to download your statement:**\n"
            "- **PhonePe** → Profile → Statement → Download PDF\n"
            "- **Paytm** → Passbook → Statement → Download"
        )
    else:
        st.success("Using built-in sample data. No upload needed.", icon="✅")

    n_clusters = st.slider(
        "Number of spending clusters",
        min_value=2, max_value=6, value=4,
        help="How many spending pattern groups KMeans should find"
    )

st.sidebar.divider()
st.sidebar.markdown("Built for **75 Days of AI** 🚀")


# ── Data loading ──────────────────────────────────────────────────────────────
@st.cache_data(show_spinner="Parsing your transactions…")
def load_data(file_bytes: bytes | None, mode: str) -> pd.DataFrame | None:
    """Load and clean transactions — PDF or sample CSV."""
    if mode == "sample":
        sample_path = os.path.join(
            os.path.dirname(__file__), "sample_transactions.csv"
        )
        return load_csv(sample_path)

    if file_bytes:
        # Write to temp file (required by pdfplumber), delete immediately after
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(file_bytes)
            tmp_path = tmp.name
        df = parse_upi_pdf(tmp_path)
        os.unlink(tmp_path)
        return df

    return None


mode = "sample" if upload_type == "Sample CSV (Demo)" else "pdf"
file_bytes = uploaded_file.read() if uploaded_file else None
df_raw = load_data(file_bytes, mode)

# Guard — nothing loaded
if df_raw is None or df_raw.empty:
    if mode == "pdf" and not uploaded_file:
        st.warning(
            "👆 Upload your PDF in the sidebar to get started.\n\n"
            "Or switch to **Sample CSV (Demo)** to see the app in action."
        )
    else:
        st.error(
            "⚠️ Could not parse this PDF. This can happen if:\n"
            "- The PDF is password-protected\n"
            "- It's a scanned image PDF (not text-based)\n"
            "- The format is different from standard PhonePe/Paytm statements\n\n"
            "Try downloading a fresh statement from the app."
        )
    st.stop()

# Run clustering
df = run_clustering(df_raw.copy(), n_clusters=n_clusters)


# ── Tabs ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(
    ["📋 Transactions", "🔵 Spending Clusters", "🚨 Biggest Leaks"]
)


# ─── TAB 1 — Transaction Table ────────────────────────────────────────────────
with tab1:
    st.subheader("📋 Your Transactions")

    total_spent = df["Amount"].sum()
    num_txns    = len(df)
    avg_txn     = df["Amount"].mean()
    top_cat     = df.groupby("Category")["Amount"].sum().idxmax()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Spent",     f"₹{total_spent:,.0f}")
    c2.metric("Transactions",    num_txns)
    c3.metric("Avg Transaction", f"₹{avg_txn:,.0f}")
    c4.metric("Top Category",    top_cat)

    st.divider()

    cats = ["All"] + sorted(df["Category"].unique().tolist())
    selected = st.selectbox("Filter by category", cats)

    display_df = df if selected == "All" else df[df["Category"] == selected]
    st.dataframe(
        display_df[["Date", "Merchant", "Amount", "Category", "DayOfWeek"]]
        .sort_values("Date", ascending=False)
        .reset_index(drop=True),
        use_container_width=True,
        hide_index=True,
    )


# ─── TAB 2 — Spending Clusters ────────────────────────────────────────────────
with tab2:
    st.subheader("🔵 Spending Clusters")
    st.caption("KMeans groups your transactions into spending behaviour patterns")

    # Personality card
    p = get_spending_personality(df)
    st.markdown(
        f"""
        <div style='background:#f0f2f6;padding:16px;border-radius:10px;margin-bottom:16px'>
            <h3>{p['emoji']} You are: <strong>{p['name']}</strong></h3>
            <p>{p['description']}</p>
            <small>Top category = <strong>{p['top_pct']}%</strong> of total spend</small>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col_a, col_b = st.columns(2)

    with col_a:
        cat_totals = df.groupby("Category")["Amount"].sum().reset_index()
        fig_pie = px.pie(
            cat_totals, names="Category", values="Amount",
            title="Spend by Category", hole=0.35,
        )
        fig_pie.update_traces(textposition="inside", textinfo="percent+label")
        fig_pie.update_layout(showlegend=False, margin=dict(t=40, b=0))
        st.plotly_chart(fig_pie, use_container_width=True)

    with col_b:
        cluster_summary = (
            df.groupby("ClusterLabel")["Amount"].sum()
            .reset_index().sort_values("Amount", ascending=True)
        )
        fig_bar = px.bar(
            cluster_summary, x="Amount", y="ClusterLabel",
            orientation="h", title="Spend by Cluster",
            labels={"Amount": "Total ₹", "ClusterLabel": ""},
        )
        fig_bar.update_layout(margin=dict(t=40, b=0))
        st.plotly_chart(fig_bar, use_container_width=True)

    # Day of week heatmap
    st.markdown("#### 📅 Spending by Day of Week")
    day_order = ["Monday","Tuesday","Wednesday","Thursday",
                 "Friday","Saturday","Sunday"]
    day_spend = (
        df.groupby("DayOfWeek")["Amount"].sum()
        .reindex(day_order, fill_value=0).reset_index()
    )
    fig_day = px.bar(
        day_spend, x="DayOfWeek", y="Amount",
        labels={"Amount": "Total ₹", "DayOfWeek": ""},
        color="Amount", color_continuous_scale="Blues",
    )
    fig_day.update_layout(coloraxis_showscale=False, margin=dict(t=10))
    st.plotly_chart(fig_day, use_container_width=True)


# ─── TAB 3 — Biggest Leaks ───────────────────────────────────────────────────
with tab3:
    st.subheader("🚨 Biggest Money Leaks")
    st.caption("Top 5 merchants eating your wallet")

    top5   = get_top_merchants(df, n=5)
    medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣"]

    for i, row in top5.iterrows():
        pct = (row["Total Spent (₹)"] / df["Amount"].sum()) * 100
        st.markdown(
            f"""
            <div style='background:#fff4f4;padding:12px 16px;
                        border-left:4px solid #ff4b4b;border-radius:6px;margin-bottom:8px'>
                {medals[i]} &nbsp; <strong>{row['Merchant']}</strong>
                &nbsp;·&nbsp; ₹{row['Total Spent (₹)']:,.0f}
                <span style='float:right;color:#888'>{pct:.1f}% of total</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.divider()

    fig_leak = px.bar(
        top5, x="Merchant", y="Total Spent (₹)",
        color="Total Spent (₹)", color_continuous_scale="Reds",
        title="Top 5 Merchants by Total Spend",
    )
    fig_leak.update_layout(coloraxis_showscale=False, margin=dict(t=40))
    st.plotly_chart(fig_leak, use_container_width=True)

    top_m  = top5.iloc[0]["Merchant"]
    top_rs = top5.iloc[0]["Total Spent (₹)"]
    st.info(
        f"💡 **Insight:** ₹{top_rs:,.0f} spent on **{top_m}** alone "
        f"({(top_rs / df['Amount'].sum() * 100):.1f}% of total). "
        f"That's your biggest leak.",
        icon="💡",
    )
