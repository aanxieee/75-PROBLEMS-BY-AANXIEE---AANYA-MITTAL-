# 💊 Medicine Dosage Estimator — Day 7/75

> *"Doctor ke paas jaane se pehle, ek rough idea toh milna chahiye na?"*

## The Story

We've all been there — someone in the family has a fever, and everyone becomes a doctor. 
*"Ek Crocin de do"*, *"Nahi nahi, uski weight zyada hai, double dose"* — sounds familiar?

Dosage isn't guesswork. It depends on your **age, weight, gender, condition severity**, and 
the type of medicine. So I built a tool that uses **Multiple Linear Regression** to estimate 
a dosage range — not as a prescription, but as an **informed starting point**.

**⚠️ This is NOT medical advice. Always consult a doctor.**

## What It Does

- **Input:** Medicine type, age, weight, gender, severity
- **Output:** Dosage range (min – predicted – max) in mg
- **Model:** Multiple Linear Regression (scikit-learn)
- **Data:** 100% synthetic — no real patient data

## Features

| Tab | What's Inside |
|-----|--------------|
| 🩺 Estimate Dosage | Input patient details → get dosage range with visual gauge |
| 🧠 How It Works | Regression formula + feature importance chart |
| 📊 Dataset | Synthetic data distributions, scatter plots, download CSV |
| ⚠️ Disclaimer | Full disclaimer — always visible banner + dedicated tab |

## Tech Stack

- **ML:** scikit-learn (LinearRegression, StandardScaler)
- **Data:** pandas, numpy
- **Viz:** plotly
- **App:** Streamlit
- **Architecture:** Modular (`src/` with separate model, preprocessor, data generator)

## Model Performance

| Metric | Value |
|--------|-------|
| R² Score | 0.889 |
| MAE | 26.59 mg |
| Training Samples | 1,200 |
| Test Samples | 300 |

## Project Structure

```
day-07-medicine-dosage-estimator/
├── app.py                  # Streamlit app (4 tabs)
├── src/
│   ├── model.py            # MLR model + range prediction
│   ├── preprocessor.py     # Encoding + scaling pipeline
│   └── data_generator.py   # Synthetic dataset generation
├── data/
│   └── dosage_data.csv     # 1500-row synthetic dataset
├── requirements.txt
├── .gitignore
└── README.md
```

## Run Locally

```bash
git clone https://github.com/aanxieee/day-07-medicine-dosage-estimator.git
cd day-07-medicine-dosage-estimator
pip install -r requirements.txt
streamlit run app.py
```

## Key Learnings

1. **Multiple Linear Regression** — when you have more than one input affecting the output
2. **Feature importance** — not all inputs matter equally (severity > weight > age)
3. **Range vs point estimate** — uncertainty matters, especially in healthcare
4. **Synthetic data** — how to generate realistic training data responsibly
5. **Disclaimers** — in healthcare ML, responsibility > accuracy

---

**Day 7/75 — AI Challenge** 🔥  
Built by [Aanya Mittal](https://github.com/aanxieee)  
*75 days. 75 builds. No excuses.*
