# 🩺 Diabetes Risk Predictor

A KNN-based diabetes risk assessment tool built with Streamlit and scikit-learn, trained on the Pima Indians Diabetes Dataset.

## What It Does

Enter 5 health indicators — **Age, BMI, Glucose, Blood Pressure, and Family History** — and get an instant risk assessment (Low / Medium / High) with a probability score.

## How It Works

- **Algorithm:** K-Nearest Neighbours (K=5, distance-weighted)
- **Dataset:** Pima Indians Diabetes Database (768 records, 8 features)
- **Features Used:** Glucose, Blood Pressure, BMI, Diabetes Pedigree Function (mapped from family history), Age
- **Preprocessing:** Zero-value imputation with median, StandardScaler normalization

### Risk Thresholds

| Probability | Risk Level |
|-------------|------------|
| < 35%       | 🟢 Low Risk |
| 35–65%      | 🟡 Medium Risk |
| > 65%       | 🔴 High Risk |

## Tech Stack

- Python 3.10+
- Streamlit
- scikit-learn (KNeighborsClassifier, StandardScaler)
- pandas, numpy

## Run Locally

```bash
git clone https://github.com/aanxieee/LV1_PROBLEM_10_DIABETES_RISK_PREDICTOR.git
cd LV1_PROBLEM_10_DIABETES_RISK_PREDICTOR
pip install -r requirements.txt
streamlit run app.py
```

## Project Structure

```
├── app.py                 # Streamlit UI
├── src/
│   ├── model.py           # KNN training + prediction
│   └── preprocessor.py    # Data loading, scaling, input mapping
├── data/
│   └── diabetes.csv       # Pima Indians Diabetes Dataset
├── requirements.txt
└── .gitignore
```

## Dataset Source

[Pima Indians Diabetes Database — Kaggle](https://www.kaggle.com/datasets/uciml/pima-indians-diabetes-database)
Originally from the National Institute of Diabetes and Digestive and Kidney Diseases.

## Disclaimer

⚠️ This tool is for **educational purposes only**. It is not a substitute for professional medical advice, diagnosis, or treatment. Always consult a qualified healthcare provider.

---

**Day 10/75 — 75 Hard Engineer Edition** 🚀
Built by [Aanya Mittal](https://github.com/aanxieee)
