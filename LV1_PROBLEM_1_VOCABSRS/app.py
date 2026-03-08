"""
Vocabulary Builder — Day 1 of 75-Day AI Challenge
Spaced Repetition System (SM-2 Algorithm)
"""

import json
import os
import random
import time
from datetime import datetime

import pandas as pd
import requests
import streamlit as st

from srs import is_due, new_word_srs, update_srs

# ─── Config ───────────────────────────────────────────────────────────────────
DATA_PATH = os.path.join(os.path.dirname(__file__), "data", "vocabulary.json")
API_BASE = "https://api.dictionaryapi.dev/api/v2/entries/en/{word}"

st.set_page_config(
    page_title="VocabSRS",
    page_icon="📚",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ─── Custom CSS ───────────────────────────────────────────────────────────────
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=DM+Sans:wght@300;400;500&display=swap');

    html, body, [class*="css"] {
        font-family: 'DM Sans', sans-serif;
    }
    h1, h2, h3 {
        font-family: 'Playfair Display', serif;
    }
    .word-card {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        border: 1px solid #0f3460;
        border-radius: 16px;
        padding: 2rem;
        margin: 1rem 0;
        color: #e0e0e0;
    }
    .word-title {
        font-family: 'Playfair Display', serif;
        font-size: 2.5rem;
        color: #e94560;
        margin-bottom: 0.25rem;
    }
    .phonetic {
        color: #a0a0c0;
        font-size: 0.9rem;
        margin-bottom: 1rem;
    }
    .definition {
        font-size: 1rem;
        line-height: 1.7;
        color: #c0c0d0;
    }
    .example {
        font-style: italic;
        color: #80809a;
        border-left: 3px solid #e94560;
        padding-left: 1rem;
        margin-top: 0.75rem;
    }
    .srs-badge {
        display: inline-block;
        padding: 0.2rem 0.6rem;
        border-radius: 20px;
        font-size: 0.78rem;
        font-weight: 500;
    }
    .badge-due   { background: #e9456022; color: #e94560; border: 1px solid #e9456044; }
    .badge-ok    { background: #4caf5022; color: #4caf50; border: 1px solid #4caf5044; }
    .stTabs [data-baseweb="tab"] {
        font-family: 'DM Sans', sans-serif;
        font-weight: 500;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ─── Data helpers ─────────────────────────────────────────────────────────────
@st.cache_data(ttl=1)
def load_vocab() -> dict:
    if not os.path.exists(DATA_PATH):
        return {}
    with open(DATA_PATH, "r") as f:
        return json.load(f)


def save_vocab(vocab: dict):
    os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)
    with open(DATA_PATH, "w") as f:
        json.dump(vocab, f, indent=2)
    load_vocab.clear()  # invalidate cache so next read picks up the write


# ─── API helper ───────────────────────────────────────────────────────────────
def fetch_word(word: str):
    """Fetch definition and example from Free Dictionary API."""
    try:
        res = requests.get(API_BASE.format(word=word.lower().strip()), timeout=8)
        if res.status_code != 200:
            return None, "Word not found. Check spelling or try another word."
        data = res.json()[0]

        definition, example, part_of_speech, phonetic = "", "", "", ""

        phonetic = data.get("phonetic", "")
        if not phonetic and data.get("phonetics"):
            phonetic = data["phonetics"][0].get("text", "")

        for meaning in data.get("meanings", []):
            defs = meaning.get("definitions", [])
            if defs:
                part_of_speech = meaning.get("partOfSpeech", "")
                definition = defs[0].get("definition", "")
                example = defs[0].get("example", "")
                if definition:
                    break

        return {
            "word": data.get("word", word),
            "phonetic": phonetic,
            "part_of_speech": part_of_speech,
            "definition": definition,
            "example": example,
        }, None

    except Exception as e:
        return None, f"Error fetching word: {str(e)}"


# ─── UI helpers ───────────────────────────────────────────────────────────────
def render_word_card(entry: dict, show_definition: bool = True):
    parts = f"<span style='color:#a0a0c0;font-size:0.85rem;'>{entry.get('part_of_speech','')}</span>" if entry.get("part_of_speech") else ""
    phonetic = f"<div class='phonetic'>{entry.get('phonetic','')}</div>" if entry.get("phonetic") else ""
    defn = f"<div class='definition'>{entry.get('definition','')}</div>" if show_definition else ""
    example = f"<div class='example'>{entry.get('example', '')}</div>" if entry.get("example") and show_definition else ""

    st.markdown(
        f"""
        <div class='word-card'>
          <div class='word-title'>{entry.get('word','')}</div>
          {phonetic}
          {parts}
          {defn}
          {example}
        </div>
        """,
        unsafe_allow_html=True,
    )


# ─── Header ───────────────────────────────────────────────────────────────────
st.markdown("## 📚 VocabSRS")
st.caption("Vocabulary builder powered by Spaced Repetition (SM-2). *Day 1 of #75DayAIChallenge*")
st.divider()

# ─── Tabs ─────────────────────────────────────────────────────────────────────
tab_add, tab_quiz, tab_words, tab_progress = st.tabs(
    ["➕ Add Word", "🧠 Quiz", "📖 My Words", "📊 Progress"]
)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — ADD WORD
# ══════════════════════════════════════════════════════════════════════════════
with tab_add:
    st.subheader("Add a New Word")
    st.write("Type any English word — definitions and examples are fetched automatically.")

    col1, col2 = st.columns([4, 1])
    with col1:
        new_word = st.text_input("Word", placeholder="e.g. ephemeral", label_visibility="collapsed")
    with col2:
        fetch_btn = st.button("Fetch →", use_container_width=True)

    if fetch_btn and new_word.strip():
        vocab = load_vocab()
        word_key = new_word.strip().lower()

        if word_key in vocab:
            st.warning(f"**{new_word}** is already in your list!")
        else:
            with st.spinner("Fetching from dictionary..."):
                entry, error = fetch_word(new_word)

            if error:
                st.error(error)
            else:
                st.success(f"Found **{entry['word']}**!")
                render_word_card(entry)

                # Save to vocab with SRS metadata
                vocab[word_key] = {**entry, **new_word_srs()}
                save_vocab(vocab)
                st.balloons()
                st.success("✅ Word saved to your vocabulary list!")

    elif fetch_btn:
        st.warning("Please enter a word first.")


# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — QUIZ
# ══════════════════════════════════════════════════════════════════════════════
with tab_quiz:
    st.subheader("Quiz Yourself")

    vocab = load_vocab()
    due_words = {k: v for k, v in vocab.items() if is_due(v)}

    if not vocab:
        st.info("No words yet. Add some words first! ➕")
    elif not due_words:
        st.success("🎉 You're all caught up! No words due for review today.")
        next_dates = [v.get("next_review", "9999") for v in vocab.values()]
        next_dates.sort()
        st.caption(f"Next review scheduled: **{next_dates[0]}**")
    else:
        st.write(f"**{len(due_words)}** word(s) due for review today.")

        # Session state for quiz
        if "quiz_word" not in st.session_state or st.session_state.get("quiz_refresh"):
            st.session_state.quiz_word = random.choice(list(due_words.keys()))
            st.session_state.quiz_revealed = False
            st.session_state.quiz_refresh = False

        quiz_key = st.session_state.quiz_word
        quiz_entry = vocab.get(quiz_key, {})

        st.markdown("**What does this word mean?**")
        render_word_card(quiz_entry, show_definition=False)

        if not st.session_state.quiz_revealed:
            if st.button("🔍 Reveal Definition", use_container_width=True):
                st.session_state.quiz_revealed = True
                st.rerun()
        else:
            render_word_card(quiz_entry, show_definition=True)
            st.markdown("---")
            st.markdown("**How well did you recall it?**")

            cols = st.columns(6)
            quality_labels = ["0\nBlackout", "1\nWrong", "2\nWrong\n(easy)", "3\nHard", "4\nHesitated", "5\nPerfect"]
            quality_colors = ["#cc0000", "#e74c3c", "#e67e22", "#f1c40f", "#2ecc71", "#27ae60"]

            selected_quality = None
            for i, col in enumerate(cols):
                with col:
                    if st.button(quality_labels[i], key=f"q_{i}", use_container_width=True):
                        selected_quality = i

            if selected_quality is not None:
                vocab = load_vocab()
                vocab[quiz_key] = update_srs(vocab[quiz_key], selected_quality)
                save_vocab(vocab)

                if selected_quality >= 3:
                    st.success(f"✅ Great! Next review in **{vocab[quiz_key]['interval']} day(s)**.")
                else:
                    st.error(f"❌ Not quite. Review again **tomorrow**.")

                time.sleep(1.5)
                st.session_state.quiz_refresh = True
                st.rerun()

        col_skip, _ = st.columns([1, 3])
        with col_skip:
            if st.button("Skip →"):
                st.session_state.quiz_refresh = True
                st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — MY WORDS
# ══════════════════════════════════════════════════════════════════════════════
with tab_words:
    st.subheader("My Word List")

    vocab = load_vocab()

    if not vocab:
        st.info("No words yet. Go add some! ➕")
    else:
        today = datetime.now().strftime("%Y-%m-%d")
        sort_option = st.selectbox("Sort by", ["Date Added (newest)", "Word (A-Z)", "Due Date"])

        items = list(vocab.items())
        if sort_option == "Word (A-Z)":
            items.sort(key=lambda x: x[0])
        elif sort_option == "Due Date":
            items.sort(key=lambda x: x[1].get("next_review", "9999"))

        st.write(f"**{len(items)} total words**")

        for word_key, entry in items:
            next_review = entry.get("next_review", "—")
            is_due_today = next_review <= today if next_review != "—" else True
            badge = (
                "<span class='srs-badge badge-due'>Due today</span>"
                if is_due_today
                else f"<span class='srs-badge badge-ok'>Review {next_review}</span>"
            )

            with st.expander(f"{entry.get('word', word_key).title()}  ·  {entry.get('part_of_speech', '')}"):
                st.markdown(
                    f"{badge} &nbsp; Interval: **{entry.get('interval', 1)}d** &nbsp; "
                    f"Ease: **{entry.get('ease_factor', 2.5):.2f}** &nbsp; "
                    f"Reviews: **{entry.get('repetitions', 0)}**",
                    unsafe_allow_html=True,
                )
                st.markdown(f"**Definition:** {entry.get('definition', 'N/A')}")
                if entry.get("example"):
                    st.markdown(f"*\"{entry['example']}\"*")

                if st.button("🗑️ Remove", key=f"del_{word_key}"):
                    vocab = load_vocab()
                    del vocab[word_key]
                    save_vocab(vocab)
                    st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 — PROGRESS
# ══════════════════════════════════════════════════════════════════════════════
with tab_progress:
    st.subheader("Your Progress")

    vocab = load_vocab()

    if not vocab:
        st.info("Nothing to show yet. Start adding words! ➕")
    else:
        today = datetime.now().strftime("%Y-%m-%d")

        total = len(vocab)
        due_today = sum(1 for v in vocab.values() if is_due(v))
        mastered = sum(1 for v in vocab.values() if v.get("repetitions", 0) >= 5)
        learning = total - mastered

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Words", total)
        c2.metric("Due Today", due_today, delta=f"-{due_today}" if due_today == 0 else None)
        c3.metric("Mastered (5+ reviews)", mastered)
        c4.metric("Still Learning", learning)

        st.divider()

        # Bar chart: words by interval bucket
        st.markdown("**Words by Review Interval**")
        buckets = {"1 day": 0, "2-6 days": 0, "1-2 weeks": 0, "3+ weeks": 0}
        for v in vocab.values():
            iv = v.get("interval", 1)
            if iv <= 1:
                buckets["1 day"] += 1
            elif iv <= 6:
                buckets["2-6 days"] += 1
            elif iv <= 14:
                buckets["1-2 weeks"] += 1
            else:
                buckets["3+ weeks"] += 1

        df = pd.DataFrame({"Interval": list(buckets.keys()), "Words": list(buckets.values())})
        st.bar_chart(df.set_index("Interval"))

        st.divider()

        # Recall quality distribution
        quality_counts = {}
        for v in vocab.values():
            q = v.get("last_quality")
            if q is not None:
                quality_counts[q] = quality_counts.get(q, 0) + 1

        if quality_counts:
            st.markdown("**Last Recall Quality Distribution**")
            q_labels = {0: "0 - Blackout", 1: "1 - Wrong", 2: "2 - Wrong (easy)",
                        3: "3 - Hard", 4: "4 - Hesitated", 5: "5 - Perfect"}
            df_q = pd.DataFrame(
                {"Quality": [q_labels[k] for k in sorted(quality_counts)],
                 "Count": [quality_counts[k] for k in sorted(quality_counts)]}
            )
            st.bar_chart(df_q.set_index("Quality"))

st.divider()
st.caption("Built with ❤️ as Day 1 of #75DayAIChallenge · SM-2 Algorithm · Free Dictionary API")
