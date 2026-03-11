# PROBLEM 4 / 75
# 🎧 Audio → Hindi Translator
### Speech-to-Text + Machine Translation
### Break the language barrier — automatically.
### Upload any audio. Get a Hindi translation in seconds.

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](#)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-blue?logo=python)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## 😤 Why I Built This

Language should never be a barrier to understanding.

Voice notes, lectures, meetings — sab English, Chinese, ya Russian mein hote hain. Aur Hindi speaker? Miss out karta hai. Subtitles dhundhne mein time waste, manually translate karna boring aur slow.

I tried online tools. Either they need API keys, paid subscriptions, ya phir aapka audio kisi third-party server pe bhejte hain. Privacy? Zero.

So I did what any engineer should — I built my own. A tool that takes *any* audio file, transcribes it locally using OpenAI Whisper, auto-detects the language, and translates the full text to Hindi — all in one click.

No API keys. No complicated setup. Upload → Transcribe → Translate. Done.

---

## 🧠 What is Whisper?

**OpenAI Whisper** is an open-source, general-purpose speech recognition model trained on 680,000 hours of multilingual audio data. It performs:

1. **Speech-to-Text** — converts spoken words into written text
2. **Language Detection** — automatically identifies the spoken language (99 languages supported)
3. **Translation** — can translate non-English speech directly to English

> Whisper runs **100% locally** — your audio never leaves your machine. No API key, no cloud dependency.

The model uses a **Transformer-based encoder-decoder** architecture, similar to what powers modern LLMs, but optimized for audio understanding.

---

## 🔬 How the Pipeline Works — The Science

The app runs a two-stage pipeline:

**Stage 1: Transcription (Whisper)**
```
Audio File (.wav/.mp3/.m4a/.ogg/.flac)
    │
    ▼
[ffmpeg preprocessing] — normalize format, sample rate
    │
    ▼
[Whisper tiny model] — local inference, 39MB
    │
    ▼
Transcript + Detected Language
```

**Stage 2: Translation (Google Translate)**
```
English/Chinese/Russian/... transcript
    │
    ▼
[googletrans 4.0.0rc1] — free Google Translate wrapper
    │
    ▼
Hindi (हिंदी) translation
```

**Whisper Model Options:**

| Model | Size | Speed | Recommended For |
|-------|------|-------|-----------------|
| tiny | 39 MB | fastest ⚡ | Streamlit Cloud, quick demos |
| base | 74 MB | fast | Better accuracy locally |
| small | 244 MB | moderate | High-quality transcription |

> Default is `tiny` — works well on Streamlit Cloud's free tier. First run downloads the model (~39MB).

---

## ✨ Features

| Step | What It Does |
|------|-------------|
| 📤 **Upload** | Drop any `.wav`, `.mp3`, `.m4a`, `.ogg`, or `.flac` — audio preview built in |
| 🎙️ **Transcribe** | OpenAI Whisper converts speech to text locally (99 languages supported) |
| 🌐 **Detect** | Language is auto-detected — no need to specify |
| 🇮🇳 **Translate** | Full text translated to Hindi via Google Translate |
| 💾 **Download** | Save transcript and/or translation as `.txt` |

**Privacy:**
- 🔒 Whisper runs **locally** — your audio never leaves your machine
- 🔒 No API keys required for transcription
- 🔒 Translation uses Google Translate API (requires internet)

---

## 🛠️ Tech Stack

| Layer | Tool |
|-------|------|
| Language | Python 3.10+ |
| Frontend | Streamlit |
| Speech-to-Text | OpenAI Whisper (local, `tiny` model) |
| Translation | googletrans 4.0.0rc1 |
| Audio Processing | ffmpeg |
| Deployment | Streamlit Cloud |

---

## 📂 Project Structure

```
LV1_PROBLEM_4_AUDIO_CONVERTER/
├── app.py              # Main Streamlit app
├── requirements.txt    # Python dependencies
├── packages.txt        # System deps (ffmpeg for Streamlit Cloud)
└── README.md
```

---

## 🚀 Run Locally

### Prerequisites
- Python 3.10+
- ffmpeg installed

```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt-get install ffmpeg

# Windows — download from https://ffmpeg.org/download.html
```

### Setup

```bash
# 1. Clone the repo
git clone https://github.com/aanxiee/75-day-ai-challenge.git
cd 75-day-ai-challenge/LV1_PROBLEM_4_AUDIO_CONVERTER

# 2. Install dependencies (Python 3.10+ recommended)
pip install -r requirements.txt

# 3. Run
streamlit run app.py
```

App opens at `http://localhost:8501`

---

## 🌐 Live Demo

👉 **Coming Soon**

---

## 💡 What I Learned

- **Whisper is shockingly good for a local model** — even the `tiny` variant handles accents, background noise, and multilingual speech surprisingly well. 39MB of pure transformer magic.
- **ffmpeg is the unsung hero** — Whisper needs clean audio input. ffmpeg handles format conversion, sample rate normalization, and codec wrangling silently in the background.
- **googletrans is fragile but free** — the unofficial Google Translate wrapper works for personal tools, but it can break with heavy usage. Good enough for a daily-use translator.
- **Streamlit Cloud + system packages** — learned that `packages.txt` is needed to install system-level dependencies like ffmpeg on Streamlit Cloud. Small detail, big headache if missed.
- **Building for yourself first** removes all friction — I shipped this because I genuinely needed multilingual audio understanding.

---

## 🔗 Links

- 🌐 Live App: *Coming Soon*
- 🐙 GitHub: [Aanya's Github](https://github.com/aanxiee)
- 💼 LinkedIn: [Check Profile](https://www.linkedin.com/in/aanya-mittal-aka-aanxiee/)
- 🌍 Website: [aanxiee](https://aanxiee.com)

---

## 📜 License

MIT — free to use, fork, and build upon.

---

*Problem 04 / 75 — 75 Problems. 75 Real-World AI Solutions. #75DayAIChallenge*
