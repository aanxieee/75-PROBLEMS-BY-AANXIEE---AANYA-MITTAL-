# 🚀 Day 01 Launch Assets — VocabSRS
## Complete execution pack: Git · LinkedIn · Instagram · Code Review · Copilot Prompt

---

---

# ① CODE REVIEW

## ✅ app.py — What's Good
- Clean tab structure, easy to extend for Day 2+
- `load_vocab()` / `save_vocab()` correctly separated from UI
- Session state quiz flow is solid
- Custom CSS is thoughtful and intentional

## 🔧 Suggested Fixes

### Fix 1 — Move `import pandas` to top of file
`import pandas as pd` is buried inside the Progress tab. Always keep imports at the top.
```python
# ❌ Current (inside tab_progress):
import pandas as pd

# ✅ Fix — move to top with other imports:
import pandas as pd
```

### Fix 2 — Add `@st.cache_data` to `load_vocab()`
Right now, `load_vocab()` reads disk on every rerun. Cache it to avoid unnecessary I/O:
```python
@st.cache_data(ttl=1)  # 1-second TTL — fast reads, still reflects saves
def load_vocab() -> dict:
    if not os.path.exists(DATA_PATH):
        return {}
    with open(DATA_PATH, "r") as f:
        return json.load(f)
```
And call `st.cache_data.clear()` inside `save_vocab()` after writing:
```python
def save_vocab(vocab: dict):
    os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)
    with open(DATA_PATH, "w") as f:
        json.dump(vocab, f, indent=2)
    load_vocab.clear()  # Invalidate cache after save
```

### Fix 3 — Quiz: handle stale word key gracefully
If a word was deleted while quiz_word is still in session state, `quiz_entry` will be `{}`.
Add a guard:
```python
quiz_key = st.session_state.quiz_word
quiz_entry = vocab.get(quiz_key)

if not quiz_entry:  # word was deleted mid-session
    st.session_state.quiz_refresh = True
    st.rerun()
```

### Fix 4 — `quality_colors` is defined but never used
```python
# ❌ Remove this unused variable:
quality_colors = ["#cc0000", "#e74c3c", "#e67e22", "#f1c40f", "#2ecc71", "#27ae60"]
```

### Fix 5 — Empty example sentence edge case in `render_word_card`
The API sometimes returns `"example": ""` (empty string), which still passes `if entry.get("example")`.
Add an explicit length check:
```python
example = (
    f"<div class='example'>\"{entry.get('example','')}\"</div>"
    if entry.get("example") and len(entry["example"].strip()) > 0 and show_definition
    else ""
)
```

---

## ✅ srs.py — Solid Implementation
The SM-2 logic is correct and clean. Two minor improvements:

### Improvement 1 — Add input validation
```python
def update_srs(word_data: dict, quality: int) -> dict:
    if not 0 <= quality <= 5:
        raise ValueError(f"Quality must be 0–5, got {quality}")
    # ... rest of function
```

### Improvement 2 — Add a `get_retention_estimate()` helper (optional, for Progress tab)
```python
def get_retention_estimate(word_data: dict) -> float:
    """
    Rough retention estimate based on interval and days since last review.
    Returns 0.0–1.0 (percentage retained).
    """
    from datetime import datetime
    last = word_data.get("last_reviewed")
    interval = word_data.get("interval", 1)
    if not last:
        return 0.0
    days_since = (datetime.now() - datetime.strptime(last, "%Y-%m-%d")).days
    # Exponential forgetting curve approximation
    retention = 0.9 ** (days_since / max(interval, 1))
    return round(min(max(retention, 0.0), 1.0), 3)
```

---
---

# ② MASTER README — Progress Table Row

Add this row to your root `75-day-ai-challenge/README.md` progress table:

```markdown
| 01 | [Vocabulary Builder](./day-01-vocabulary-builder/) | Spaced Repetition (SM-2) | Personal / Productivity | [🔗 Live Demo](https://your-app-link.streamlit.app) | ✅ |
```

Full table template (copy this as your master README table starter):

```markdown
## 📅 Challenge Progress

| Day | Project | Technique / Concept | Domain | Demo | Status |
|-----|---------|-------------------|--------|------|--------|
| 01 | [Vocabulary Builder](./day-01-vocabulary-builder/) | Spaced Repetition (SM-2) | Personal / Productivity | [🔗 Live](https://your-app-link.streamlit.app) | ✅ |
| 02 | Coming soon... | — | Fintech | — | 🔜 |
```

---
---

# ③ GIT COMMANDS — Exact Copy-Paste

## First-time setup (run once)
```bash
# Navigate to your project folder
cd path/to/your/75-day-ai-challenge

# Initialize git
git init

# Connect to your GitHub remote
git remote add origin https://github.com/aanxiee/75-day-ai-challenge.git

# Verify remote
git remote -v
```

## Push Day 1
```bash
# Stage everything in the Day 1 folder
git add day-01-vocabulary-builder/

# Also stage root README if you updated the progress table
git add README.md

# Commit with standard message format
git commit -m "Day 01: Vocabulary Builder with Spaced Repetition (SM-2)

- Built word-saving feature with Free Dictionary API integration
- Implemented SM-2 algorithm for spaced repetition in srs.py
- 4-tab Streamlit UI: Add Word, Quiz, My Words, Progress
- Deployed on Streamlit Cloud
- Part of #75DayAIChallenge"

# Push to GitHub
git push -u origin main
```

## Day-to-day workflow (from Day 2 onwards)
```bash
git add day-0X-project-name/
git add README.md
git commit -m "Day 0X: [Project Name] with [Technique]"
git push
```

---
---

# ④ LINKEDIN POST — Final Version

```
Day 1/75 — I built a Vocabulary Builder because I kept forgetting every new word I read.

The problem was embarrassingly relatable:
→ Read "ephemeral" in an article
→ Look it up, understand it
→ Forget it by next week
→ Repeat forever

So I built VocabSRS using Spaced Repetition (SM-2) — the same science behind Anki and Duolingo.

Here's how SM-2 works in one sentence:
It shows you a word just before you're about to forget it, then pushes the next review further and further apart as you get better at it.

What I shipped today:
→ Type a word → auto-fetch definition + example sentence (Free Dictionary API)
→ Rate your recall 0–5 after each quiz
→ SM-2 calculates your next review date instantly
→ Progress dashboard with retention stats
→ Deployed live on Streamlit

This is Day 1 of my 75-day challenge: one real-world AI/ML project every single day, focused on problems I personally face.

Day 2 is in Fintech. See you tomorrow.

🔗 Live demo: [your-streamlit-link]
🐙 GitHub: https://github.com/aanxiee/75-day-ai-challenge
🌍 Website: aanxiee.com

#75DayAIChallenge #MachineLearning #BuildInPublic #Python #Streamlit #AIEngineer
```

---
---

# ⑤ INSTAGRAM — Caption + Reel Script

## Caption
```
Day 1/75 ✅

Built a vocab app because I kept forgetting words I read 😭
SM-2 algorithm + Python + 1 day = this 👇

Link in bio 🔗

#75DayChallenge #AIEngineer #PythonProject #BuildInPublic #LearnInPublic
```

---

## Reel Script — 60 Seconds

**[0–4s] — HOOK (text on screen, no talking)**
> "I keep forgetting every new word I read."
> *Show: scrolling through an article, highlighting "ephemeral"*

**[4–10s] — THE PROBLEM**
> VO: "I'd look up a word, understand it — gone by next week."
> *Show: phone notes with a graveyard of vocabulary lists, unused*

**[10–18s] — THE SOLUTION**
> VO: "So I used the same algorithm that Duolingo and Anki use — SM-2 Spaced Repetition."
> *Text overlay: "SM-2 = review just before you forget"*

**[18–38s] — DEMO (screen record)**
> VO: "Type a word. Instant definition. Then the app quizzes you."
> *Show: typing "ephemeral" → definition appears → Quiz tab → 0-5 rating buttons*
> *Show: "Next review in 6 days" message appearing*

**[38–50s] — IT'S LIVE**
> *Show: opening the Streamlit link on phone*
> VO: "Deployed in one day. Works on any device."
> *Show: Progress tab with stats and charts*

**[50–58s] — CLOSE**
> *Cut to: text screen*
> "Day 1 of 75."
> "75 problems. 75 real-world AI solutions."
> "GitHub + link in bio."

**[58–60s] — HOOK FOR TOMORROW**
> "Day 2 is Fintech. See you tomorrow."

---
---

# ⑥ VS CODE COPILOT PROMPT — Reusable Template

Save this as a snippet. Use it at the start of every new day:

```
I am building a project for Day [X] of my 75-day AI challenge.

Project: [Project Name]
Technique: [e.g. Linear Regression / CNN / RAG / SM-2 / LSTM]
Domain: [e.g. Fintech / Healthcare / Productivity]
Stack: Python, Streamlit, [any extra library e.g. scikit-learn, pandas, transformers]

Folder structure:
day-0X-[project-name]/
├── app.py              (Streamlit UI)
├── model/
│   └── train.py        (training or core logic script, if needed)
├── data/
│   └── [sample data or .json store]
├── requirements.txt
└── README.md

Build this step by step:
1. Write requirements.txt first (minimum dependencies only)
2. Build core logic in model/ or a separate .py file
3. Build the Streamlit UI in app.py with clean tabs
4. Write README.md with: problem statement, how it works, run instructions, what I learned

Code standards:
- Clean, commented, beginner-readable
- Type hints on all functions
- Each function does one thing
- No hardcoded paths — use os.path
- Error handling for API calls and file I/O

Start with requirements.txt.
```

---

*All assets ready. Ship it. 🚀*
*Day 01 / 75 — #75DayAIChallenge | aanxiee.com*
