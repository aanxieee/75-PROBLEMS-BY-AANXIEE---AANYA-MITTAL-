"""
Visualization module for Financial News Sentiment Analyzer.
Plotly charts: gauge, bar, pie, trend line.
"""

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from src.sentiment_analyzer import SentimentResult


# Consistent color palette
COLORS = {
    "positive": "#00C853",
    "negative": "#FF1744",
    "neutral": "#607D8B",
    "buy": "#00C853",
    "sell": "#FF1744",
    "hold": "#FFC107",
    "bg": "rgba(0,0,0,0)",
    "text": "#E0E0E0",
    "grid": "#333333",
}


def confidence_gauge(result: SentimentResult) -> go.Figure:
    """Semicircular gauge showing confidence + signal."""
    color = (
        COLORS["buy"] if result.signal == "BUY"
        else COLORS["sell"] if result.signal == "SELL"
        else COLORS["hold"]
    )

    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=result.confidence,
        number={"suffix": "%", "font": {"size": 42, "color": COLORS["text"]}},
        title={
            "text": f"Signal: {result.signal}",
            "font": {"size": 20, "color": color},
        },
        gauge={
            "axis": {"range": [0, 100], "tickcolor": COLORS["text"]},
            "bar": {"color": color},
            "bgcolor": COLORS["grid"],
            "steps": [
                {"range": [0, 33], "color": "#1a1a2e"},
                {"range": [33, 66], "color": "#16213e"},
                {"range": [66, 100], "color": "#0f3460"},
            ],
            "threshold": {
                "line": {"color": "#FFFFFF", "width": 2},
                "thickness": 0.8,
                "value": result.confidence,
            },
        },
    ))

    fig.update_layout(
        height=280,
        margin=dict(l=30, r=30, t=60, b=20),
        paper_bgcolor=COLORS["bg"],
        plot_bgcolor=COLORS["bg"],
        font={"color": COLORS["text"]},
    )
    return fig


def score_breakdown_bar(result: SentimentResult) -> go.Figure:
    """Horizontal bar showing pos/neg/neu breakdown."""
    fig = go.Figure()

    categories = ["Positive", "Neutral", "Negative"]
    values = [result.positive, result.neutral, result.negative]
    bar_colors = [COLORS["positive"], COLORS["neutral"], COLORS["negative"]]

    fig.add_trace(go.Bar(
        y=categories,
        x=values,
        orientation="h",
        marker_color=bar_colors,
        text=[f"{v:.1%}" for v in values],
        textposition="auto",
        textfont={"size": 14},
    ))

    fig.update_layout(
        title={"text": "Score Breakdown", "font": {"size": 16}},
        height=220,
        margin=dict(l=10, r=10, t=40, b=10),
        paper_bgcolor=COLORS["bg"],
        plot_bgcolor=COLORS["bg"],
        font={"color": COLORS["text"]},
        xaxis={"range": [0, 1], "showgrid": False, "visible": False},
        yaxis={"showgrid": False},
    )
    return fig


def bulk_sentiment_chart(results: list[SentimentResult]) -> go.Figure:
    """Bar chart of compound scores for all headlines."""
    if not results:
        return go.Figure()

    labels = [
        r.headline[:50] + "..." if len(r.headline) > 50 else r.headline
        for r in results
    ]
    compounds = [r.compound for r in results]
    colors = [
        COLORS["positive"] if c >= 0.05
        else COLORS["negative"] if c <= -0.05
        else COLORS["neutral"]
        for c in compounds
    ]

    fig = go.Figure(go.Bar(
        x=list(range(1, len(results) + 1)),
        y=compounds,
        marker_color=colors,
        text=[f"{c:+.2f}" for c in compounds],
        textposition="outside",
        textfont={"size": 11},
        hovertext=labels,
        hoverinfo="text+y",
    ))

    fig.update_layout(
        title={"text": "Headline Sentiment Scores", "font": {"size": 16}},
        xaxis_title="Headline #",
        yaxis_title="Compound Score",
        yaxis={"range": [-1.1, 1.1], "gridcolor": COLORS["grid"]},
        xaxis={"gridcolor": COLORS["grid"]},
        height=400,
        margin=dict(l=10, r=10, t=50, b=10),
        paper_bgcolor=COLORS["bg"],
        plot_bgcolor=COLORS["bg"],
        font={"color": COLORS["text"]},
    )
    return fig


def sentiment_pie(results: list[SentimentResult]) -> go.Figure:
    """Pie chart of sentiment distribution."""
    pos = sum(1 for r in results if r.label == "Positive")
    neg = sum(1 for r in results if r.label == "Negative")
    neu = sum(1 for r in results if r.label == "Neutral")

    fig = go.Figure(go.Pie(
        labels=["Positive", "Negative", "Neutral"],
        values=[pos, neg, neu],
        marker=dict(colors=[COLORS["positive"], COLORS["negative"], COLORS["neutral"]]),
        hole=0.4,
        textinfo="label+percent",
        textfont={"size": 13},
    ))

    fig.update_layout(
        title={"text": "Sentiment Distribution", "font": {"size": 16}},
        height=350,
        margin=dict(l=10, r=10, t=50, b=10),
        paper_bgcolor=COLORS["bg"],
        plot_bgcolor=COLORS["bg"],
        font={"color": COLORS["text"]},
        showlegend=False,
    )
    return fig


def sentiment_trend(history: list[dict]) -> go.Figure:
    """Line chart of sentiment over time (session-based)."""
    if not history:
        return go.Figure()

    df = pd.DataFrame(history)

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df["index"],
        y=df["compound"],
        mode="lines+markers",
        line={"width": 2.5, "color": "#448AFF"},
        marker={
            "size": 8,
            "color": [
                COLORS["positive"] if c >= 0.05
                else COLORS["negative"] if c <= -0.05
                else COLORS["neutral"]
                for c in df["compound"]
            ],
            "line": {"width": 1, "color": "#FFFFFF"},
        },
        hovertext=df.get("headline", ""),
        hoverinfo="text+y",
        name="Compound",
    ))

    # Zero line
    fig.add_hline(y=0, line_dash="dash", line_color="#666666", line_width=1)
    # Threshold lines
    fig.add_hline(y=0.05, line_dash="dot", line_color=COLORS["positive"],
                  line_width=0.8, opacity=0.5)
    fig.add_hline(y=-0.05, line_dash="dot", line_color=COLORS["negative"],
                  line_width=0.8, opacity=0.5)

    fig.update_layout(
        title={"text": "Sentiment Trend (Session)", "font": {"size": 16}},
        xaxis_title="Analysis #",
        yaxis_title="Compound Score",
        yaxis={"range": [-1.1, 1.1], "gridcolor": COLORS["grid"]},
        xaxis={"gridcolor": COLORS["grid"]},
        height=350,
        margin=dict(l=10, r=10, t=50, b=10),
        paper_bgcolor=COLORS["bg"],
        plot_bgcolor=COLORS["bg"],
        font={"color": COLORS["text"]},
        showlegend=False,
    )
    return fig
