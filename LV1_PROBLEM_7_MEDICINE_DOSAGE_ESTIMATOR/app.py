"""
💊 Medicine Dosage Estimator — Day 7/75 AI Challenge
Multiple Linear Regression | Streamlit App
⚠️ NOT medical advice. Synthetic data only. Always consult a doctor.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from src.model import DosageModel
from src.data_generator import generate_dataset

# ──────────────────────────────────────────────
# Page Config
# ──────────────────────────────────────────────
st.set_page_config(
    page_title="💊 Dosage Estimator",
    page_icon="💊",
    layout="wide",
)

# Persistent disclaimer banner
st.markdown(
    """
    <div style="background-color:#FF4B4B22; border-left:4px solid #FF4B4B;
    padding:10px 16px; border-radius:4px; margin-bottom:16px;">
    ⚠️ <strong>Disclaimer:</strong> This is an <strong>estimator using synthetic data</strong> — 
    NOT medical advice. Always consult a qualified healthcare professional for dosage decisions.
    </div>
    """,
    unsafe_allow_html=True,
)

st.title("💊 Medicine Dosage Estimator")
st.caption("Day 7/75 — AI Challenge | Multiple Linear Regression")

# ──────────────────────────────────────────────
# Init model (cached)
# ──────────────────────────────────────────────
@st.cache_resource
def load_model():
    model = DosageModel()
    df = generate_dataset()
    metrics = model.train(df)
    return model, df, metrics

model, dataset, metrics = load_model()

# ──────────────────────────────────────────────
# Tabs
# ──────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "🩺 Estimate Dosage",
    "🧠 How It Works",
    "📊 Dataset",
    "⚠️ Disclaimer",
])

# ──────────────────────────────────────────────
# Tab 1: Estimate Dosage
# ──────────────────────────────────────────────
with tab1:
    st.subheader("Enter Patient Details")

    col1, col2 = st.columns(2)

    with col1:
        medicine_type = st.selectbox(
            "Medicine Category",
            ["Painkiller", "Antibiotic", "General OTC"],
            help="Select the type of medicine",
        )
        age = st.slider("Age (years)", 18, 80, 35)
        weight = st.slider("Weight (kg)", 40.0, 130.0, 70.0, step=0.5)

    with col2:
        gender = st.radio("Gender", ["Male", "Female"], horizontal=True)
        severity = st.select_slider(
            "Condition Severity",
            options=["Mild", "Moderate", "Severe"],
            value="Moderate",
        )

    st.markdown("---")

    if st.button("🔍 Estimate Dosage", type="primary", use_container_width=True):
        min_mg, predicted, max_mg = model.predict_range(
            age=age,
            weight=weight,
            gender=gender,
            severity=severity,
            medicine_type=medicine_type,
        )

        # Results
        st.markdown("### Estimated Dosage Range")

        col_a, col_b, col_c = st.columns(3)
        col_a.metric("🔽 Min", f"{min_mg} mg")
        col_b.metric("🎯 Predicted", f"{predicted} mg")
        col_c.metric("🔼 Max", f"{max_mg} mg")

        # Visual gauge
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=predicted,
            title={"text": f"{medicine_type} Dosage (mg)"},
            gauge={
                "axis": {"range": [max(0, min_mg - 50), max_mg + 50]},
                "bar": {"color": "#636EFA"},
                "steps": [
                    {"range": [max(0, min_mg - 50), min_mg], "color": "#E8F0FE"},
                    {"range": [min_mg, max_mg], "color": "#C6DCFE"},
                    {"range": [max_mg, max_mg + 50], "color": "#E8F0FE"},
                ],
                "threshold": {
                    "line": {"color": "#FF4B4B", "width": 3},
                    "thickness": 0.8,
                    "value": predicted,
                },
            },
        ))
        fig.update_layout(height=280, margin=dict(t=60, b=20, l=30, r=30))
        st.plotly_chart(fig, use_container_width=True)

        st.info(
            f"📋 **Input Summary:** {medicine_type} | {age}y | {weight}kg | "
            f"{gender} | {severity} severity"
        )

        st.warning(
            "⚠️ This is a synthetic estimate. Real dosage depends on many more "
            "clinical factors. **Always consult your doctor.**"
        )

# ──────────────────────────────────────────────
# Tab 2: How It Works
# ──────────────────────────────────────────────
with tab2:
    st.subheader("🧠 How Multiple Linear Regression Works")

    st.markdown(
        """
        **Multiple Linear Regression** finds the best-fit linear relationship between 
        multiple input features and a continuous output (dosage).

        The model learns a formula like:
        """
    )

    st.code(model.get_formula_string(), language="text")

    st.markdown(
        """
        > *Note: These coefficients are on **scaled** features (mean=0, std=1), 
        so they represent relative importance, not raw mg-per-unit.*
        """
    )

    # Feature importance chart
    st.markdown("### Feature Importance")
    importance = model.get_feature_importance()

    fig = px.bar(
        importance,
        x="abs_importance",
        y="feature",
        orientation="h",
        color="coefficient",
        color_continuous_scale="RdBu_r",
        labels={"abs_importance": "Absolute Coefficient", "feature": "Feature"},
    )
    fig.update_layout(height=350, yaxis={"categoryorder": "total ascending"})
    st.plotly_chart(fig, use_container_width=True)

    # Model metrics
    st.markdown("### Model Performance")
    mcol1, mcol2, mcol3 = st.columns(3)
    mcol1.metric("R² Score", metrics["r2_score"])
    mcol2.metric("Mean Abs Error", f"{metrics['mae']} mg")
    mcol3.metric("Residual Std", f"{metrics['residual_std']} mg")

    st.caption(
        f"Trained on {metrics['train_samples']} samples | "
        f"Tested on {metrics['test_samples']} samples"
    )

# ──────────────────────────────────────────────
# Tab 3: Dataset
# ──────────────────────────────────────────────
with tab3:
    st.subheader("📊 Synthetic Dataset")

    st.info(
        "🧪 This dataset is **100% synthetic** — generated using controlled formulas "
        "with added noise. No real patient data was used."
    )

    # Quick stats
    st.markdown("### Distribution Overview")

    dcol1, dcol2 = st.columns(2)

    with dcol1:
        fig = px.histogram(
            dataset, x="dosage_mg", color="medicine_type",
            barmode="overlay", nbins=40, opacity=0.7,
            title="Dosage Distribution by Medicine Type",
        )
        fig.update_layout(height=350)
        st.plotly_chart(fig, use_container_width=True)

    with dcol2:
        fig = px.box(
            dataset, x="severity", y="dosage_mg", color="gender",
            title="Dosage by Severity & Gender",
        )
        fig.update_layout(height=350)
        st.plotly_chart(fig, use_container_width=True)

    # Scatter
    fig = px.scatter(
        dataset, x="weight_kg", y="dosage_mg", color="medicine_type",
        size="age", opacity=0.5, hover_data=["severity", "gender"],
        title="Weight vs Dosage (size = age)",
    )
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)

    # Raw data
    st.markdown("### Sample Data")
    st.dataframe(dataset.head(50), use_container_width=True, height=300)

    csv = dataset.to_csv(index=False)
    st.download_button(
        "📥 Download Full Dataset (CSV)",
        csv,
        "dosage_data_synthetic.csv",
        "text/csv",
    )

# ──────────────────────────────────────────────
# Tab 4: Disclaimer
# ──────────────────────────────────────────────
with tab4:
    st.subheader("⚠️ Important Disclaimer")

    st.error(
        """
        **This application is NOT a substitute for professional medical advice.**
        
        Please read carefully:
        """
    )

    st.markdown(
        """
        1. **Synthetic Data Only** — The model is trained on artificially generated data. 
           It does NOT reflect real clinical guidelines or pharmacological research.
        
        2. **Not FDA Approved** — This tool has no medical certification or approval 
           from any regulatory body.
        
        3. **Educational Purpose** — Built as part of a 75-day AI/ML learning challenge 
           to demonstrate Multiple Linear Regression concepts.
        
        4. **Consult a Doctor** — Always consult a qualified healthcare professional 
           before taking any medication. Dosage depends on your complete medical history, 
           current medications, allergies, organ function, and many other factors this 
           tool cannot account for.
        
        5. **No Liability** — The creator assumes no responsibility for any decisions 
           made based on this tool's output.
        """
    )

    st.markdown("---")
    st.markdown(
        """
        **Built with ❤️ by [Aanya Mittal](https://github.com/aanxieee)**  
        Day 7/75 — AI Challenge  
        *"ML in healthcare is powerful, but responsibility comes first."*
        """
    )
