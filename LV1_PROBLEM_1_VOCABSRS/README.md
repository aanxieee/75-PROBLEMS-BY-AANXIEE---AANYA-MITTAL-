<img width="1908" height="963" alt="{7D55FA1D-5AEE-40E9-B2F7-9CA632EE31FC}" src="https://github.com/user-attachments/assets/d7ec56b2-01cd-4710-adb1-7e8aad79bbe6" 
/>
# PROBLEM 1 / 75
#  VocabSRS — Vocabulary Builder with Spaced Repetition
### No ML. Just logic.
### Spaced Repetition doesn't need a model.
### Sometimes the best solution is the simplest one.

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://vocab-srs-1-aanxiee.streamlit.app/)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-blue?logo=python)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## 😤 Why I Built This

Roz ek naya word padhti thi — articles mein, research papers mein, LinkedIn posts mein. Lookup karti thi, "oh interesting!" bolti thi, and by next week? Gone. Completely forgotten.

I tried Anki. Too manual, too rigid. I tried highlight-and-save. Graveyard of good intentions.

So I did what any engineer should — I built my own. A vocabulary app that fits *my* exact reading workflow: paste a word, get the definition instantly, and get quizzed at the *exact* right moment using actual memory science.

This is that app.

---

## 🧠 What is Spaced Repetition?

Spaced Repetition exploits the **forgetting curve** — the scientifically observed fact that memories fade predictably over time. Instead of reviewing all your words every day (exhausting and inefficient), the system shows you a word *just before you're about to forget it* — gradually pushing the review gap wider and wider as your retention improves.

> Review a word right → wait longer next time.
> Forget a word → reset and review tomorrow.

This is the same science powering **Anki**, **Duolingo**, and medical school flashcard systems used worldwide.

---

## 🔬 SM-2 Algorithm — How It Works

This app implements **SM-2** by Piotr Wozniak (1987) — the original, battle-tested algorithm.

After each recall attempt, you rate yourself **0–5**:

| Rating | Meaning |
|--------|---------|
| 0 | Complete blackout |
| 1 | Wrong — barely remembered |
| 2 | Wrong — but felt easy |
| 3 | Correct, but hard |
| 4 | Correct after hesitation |
| 5 | Perfect recall |

**The math:**
```python
# Ease factor update (min: 1.3)
ease_factor += 0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02)

# Interval progression
if repetitions == 0: interval = 1    # day
elif repetitions == 1: interval = 6  # days
else: interval = round(interval * ease_factor)
```

- **Quality < 3** → interval resets to 1 day (review tomorrow)
- **Quality ≥ 3** → interval grows exponentially
- **Ease Factor** adjusts per word — harder words reviewed more often, easy words reviewed less

---

## ✨ Features

| Tab | What It Does |
|-----|-------------|
| ➕ **Add Word** | Type any word → auto-fetches definition, phonetic, part of speech, and example sentence from Free Dictionary API |
| 🧠 **Quiz** | Shows word → you recall → reveal definition → rate 0–5 → SM-2 updates next review date instantly |
| 📖 **My Words** | Full list with SRS stats per word: interval, ease factor, repetition count. Sort by date, A–Z, or due date |
| 📊 **Progress** | Stats dashboard: total words, due today, mastered (5+ reviews), interval distribution chart, recall quality chart |

---

## 🛠️ Tech Stack

| Layer | Tool |
|-------|------|
| Language | Python 3.10+ |
| Frontend | Streamlit |
| Storage | JSON (no database needed) |
| Dictionary API | [Free Dictionary API](https://dictionaryapi.dev/) |
| Algorithm | SM-2 Spaced Repetition |
| Deployment | Streamlit Cloud |

---

## 📂 Project Structure

```
day-01-vocabulary-builder/
├── app.py               # Main Streamlit app (4 tabs)
├── srs.py               # SM-2 algorithm logic
├── data/
│   └── vocabulary.json  # Word store + SRS metadata (auto-created)
├── requirements.txt
└── README.md
```

---

## 🚀 Run Locally

```bash
# 1. Clone the repo
git clone https://github.com/aanxiee/75-day-ai-challenge.git
cd 75-day-ai-challenge/day-01-vocabulary-builder

# 2. Install dependencies (Python 3.10+ recommended)
pip install -r requirements.txt

# 3. Run
streamlit run app.py
```

App opens at `http://localhost:8501`

---

## 🌐 Live Demo

👉 **[Try the app live on Streamlit Cloud](https://vocab-srs-1-aanxiee.streamlit.app/)**

---

## 💡 What I Learned

- **SM-2 is surprisingly simple** — 5 lines of math, decades of research. Understanding *why* it works made the implementation feel meaningful.
- **Streamlit session state** requires deliberate design — managing quiz state across reruns taught me to think about UI as a state machine.
- **JSON is enough** — for personal tools, a flat file beats a database. Simplicity is a feature.
- **Building for yourself first** removes all friction — I shipped this because I genuinely needed it.

---

## 🔗 Links

- 🌐 Live App: [your-app-link.streamlit.app](https://vocab-srs-1-aanxiee.streamlit.app/))
- 🐙 GitHub: [github.com/aanxiee/75-day-ai-challenge](https://github.com/aanxiee)
- 💼 LinkedIn: [lnkd.in/gDJzaXnK]((https://www.linkedin.com/in/aanya-mittal-aka-aanxiee/))
- 🌍 Website: [aanxiee.com](https://aanxiee.com)

---

## 📜 License

MIT — free to use, fork, and build upon.

---

*Day 01 / 75 — 75 Problems. 75 Real-World AI Solutions. #75DayAIChallenge*
