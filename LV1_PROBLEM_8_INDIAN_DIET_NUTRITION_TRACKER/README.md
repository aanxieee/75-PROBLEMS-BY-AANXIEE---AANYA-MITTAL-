# 🍛 Indian Diet Nutrition Tracker

**Track your daily Indian food intake → see nutrition gaps → get smart dinner suggestions.**

No more guessing — log your dal, roti, sabzi and see exactly what's missing in your diet today.

---

## Features

- **🔍 Smart Food Search** — 74 curated Indian foods across 12 categories (dals, sabzis, rotis, dairy, fruits, South Indian, snacks & more)
- **📊 12-Nutrient Dashboard** — Track Calories, Protein, Carbs, Fats, Fiber, Calcium, Iron, Zinc, Vitamins A/B12/C/D with visual progress bars
- **🎯 Personalized Targets** — Mifflin-St Jeor BMR → TDEE calculation based on your age, weight, height, gender, activity level & goal
- **💡 Smart Suggestions** — Rule-based Hinglish recommendations: "Protein kam hai — paneer ya dal lo 💪"
- **📋 Food Log** — Add, view, remove entries by meal (Breakfast/Lunch/Snack/Dinner)
- **💾 SQLite Persistence** — Data persists across sessions, no login needed
- **📱 Mobile-Friendly** — Custom CSS optimized for phone screens

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Frontend | Streamlit |
| Database | SQLite3 |
| Language | Python 3.10+ |
| Data | Custom curated Indian food nutrition JSON |

## Project Structure

```
day-08-indian-diet-tracker/
├── app.py                    # Main Streamlit application
├── src/
│   ├── food_database.py      # Indian foods loader + search
│   ├── tracker.py            # SQLite persistence (profile + food log)
│   ├── calculator.py         # BMR/TDEE + personalized nutrient targets
│   └── recommender.py        # Rule-based meal suggestions
├── data/
│   └── indian_foods.json     # 74 Indian foods × 12 nutrients
├── requirements.txt
├── .gitignore
└── README.md
```

## Quick Start

```bash
# Clone
git clone https://github.com/aanxieee/day-08-indian-diet-tracker.git
cd day-08-indian-diet-tracker

# Install
pip install -r requirements.txt

# Run
streamlit run app.py
```

## How It Works

1. **Set up profile** — Enter age, weight, height, gender, activity level, and goal
2. **Log your food** — Search or browse Indian foods, select portion, add to meal
3. **Check dashboard** — Color-coded progress bars show exactly where you stand
4. **Get suggestions** — App tells you what to eat next based on current deficits
5. **Repeat daily** — Data persists in SQLite, track across days

## Nutrition Targets

- **BMR**: Mifflin-St Jeor equation
- **TDEE**: BMR × activity multiplier
- **Macros**: Goal-based split (e.g., deficit = 30% protein, 40% carbs, 30% fats)
- **Micronutrients**: ICMR-NIN 2020 RDA values for Indian population

## Indian Food Database

74 foods with per-serving nutrition across 12 categories:
Dals & Pulses • Rotis & Breads • Rice & Grains • Sabzi & Curries • Dairy • Proteins & Snacks • South Indian • Fruits • Beverages • Salads & Sides • Snacks • Sweets & Desserts

## Screenshots

*Coming soon after deployment*

---

### Day 08/75 — Healthcare Domain | 75 Hard Engineer Edition 🔥
Built by [@aanxieee](https://github.com/aanxieee)
