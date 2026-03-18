# 🎧 Audio → Hindi Translator

### Aanya's 75-Day AI Challenge · Day 04 / 75

> **One real problem. One AI solution.**  
> Break the language barrier — transcribe any audio and translate to Hindi automatically.

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://audio-hindi-translator-aanxiee.streamlit.app/)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-blue?logo=python)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## 😤 Why I Built This (Personal Story)

Voice notes in English. Lectures in Chinese. Meetings in Russian. Podcasts in Spanish.

Me? Hindi speaker. Every time someone shares audio in another language, I either:
1. Find transcripts manually (if lucky)
2. Spend 20 minutes translating (if lucky, again)
3. Give up and miss out completely

I tried online tools — most require API keys, paid subscriptions, or worse — they send your **personal audio to third-party servers**. Privacy gone. Trust = 0.

So I built my own — a tool that takes *any* audio file, transcribes it **locally** using OpenAI Whisper, auto-detects the language, and translates it all to Hindi in seconds.

**No API keys. No cloud uploads. No subscriptions. Just pure, private, linguistic superpowers.**

---

## 🧠 How It Works

### The Science Behind Whisper

**OpenAI Whisper** is an open-source speech recognition model trained on **680,000 hours** of multilingual audio data. It:

1. **Transcribes speech** to text (99 languages supported)
2. **Auto-detects language** — no manual input needed  
3. **Handles accents, background noise, and technical jargon** — trained on diverse real-world audio

> ✅ **Runs 100% locally** — your audio never leaves your machine. No API. No cloud. No tracking.

### The Pipeline

```
Audio File (.wav, .mp3, .m4a, .ogg, .flac)
    ↓
[ffmpeg] Normalize format & sample rate (22.05 kHz)
    ↓
[Whisper STT] Transcribe speech → text (locally, 39-244 MB depending on model)
    ↓
Auto-detect spoken language (99 languages)
    ↓
[Google Translate] Translate transcript → Hindi (हिंदी)
    ↓
Display + Download (transcript + translation)
```

### Whisper Model Sizes

| Model | Size | Speed | Best For |
|-------|------|-------|----------|
| **tiny** | 39 MB | ⚡ Fastest | Streamlit Cloud (free tier) |
| **base** | 74 MB | 🚀 Fast | Local running (good balance) |
| **small** | 244 MB | 🎯 High accuracy | Professional transcription |

Default: **tiny** (first run downloads ~39 MB, then cached).

---

## ✨ Features

| Tab | What It Does |
|-----|-------------|
| 📤 **Upload** | Drag & drop any audio file (.wav, .mp3, .m4a, .ogg, .flac) |
| 📝 **Transcribe** | OpenAI Whisper converts speech → text (99 languages) |
| 🌐 **Detect** | Language automatically identified (English, Hindi, Chinese, Spanish, etc.) |
| 🇮🇳 **Translate** | Full transcript translated to Hindi via Google Translate |
| 💾 **Download** | Save transcript and/or translation as `.txt` files |

### Privacy Features

🔒 **Your audio stays private:**
- Whisper runs on **your machine** — no upload to OpenAI
- Only transcription text is sent to Google Translate API (not audio)
- No login required. No tracking. No ads.

---

## 🛠️ Tech Stack

| Layer | Tool | Why? |
|-------|------|------|
| **Frontend** | Streamlit | Fast, zero JavaScript needed |
| **Speech-to-Text** | OpenAI Whisper | Open-source, accurate, 99 languages, runs locally |
| **Translation** | googletrans 4.0.0rc1 | Free, no API key, supports 100+ languages |
| **Audio Processing** | ffmpeg | Industry standard for format conversion |
| **Language** | Python 3.10+ | Simple, powerful, huge ML ecosystem |
| **Deployment** | Streamlit Cloud | Free, built for Streamlit apps |

---

## 🚀 Run Locally

### Prerequisites
- Python 3.10 or higher
- `ffmpeg` installed ([download here](https://ffmpeg.org/download.html) or `brew install ffmpeg` on macOS)

### Step-by-step

```bash
# 1. Navigate to project folder
cd LV1_PROBLEM_4

# 2. Create virtual environment
python -m venv .venv

# 3. Activate it
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Run the app
streamlit run app.py
```

**App opens automatically at:** `http://localhost:8501`

---

## 🌐 Live Demo

Try it online (first run may take 30 seconds as Whisper downloads):

👉 **[Audio → Hindi Translator on Streamlit Cloud](https://audio-hindi-translator-aanxiee.streamlit.app/)**

---

## 📂 Project Structure

```
LV1_PROBLEM_4/
├── app.py             ← Main Streamlit application
├── requirements.txt   ← Python dependencies
├── .gitignore         ← Git ignore rules (audio files excluded)
└── README.md          ← This file
```

Simple, flat structure — no subfolders. Everything at root level.

---

## 💡 What I Learned

1. **Whisper is insanely accurate** — even with heavy background noise, accents, and fast speech. The transformer architecture can really *understand* speech.

2. **Local inference > cloud APIs** — Running Whisper locally means:
   - No latency
   - No API costs
   - 100% privacy
   - Works offline (except for translation)

3. **Language detection is automatic** — Whisper doesn't just transcribe; it tells you what language it heard. No need for user input.

4. **googletrans is fragile but works** — Google Translate API is rate-limited and sometimes breaks, but for personal projects it's free and good enough.

5. **UX matters as much as ML** — The app's real value isn't the algorithms; it's the fact that uploading audio → getting Hindi translation takes 3 seconds and feels frictionless.

---

## 🔗 Links

- 🌐 **Live App**: [audio-hindi-translator-aanxiee.streamlit.app](https://audio-hindi-translator-aanxiee.streamlit.app/)
- 🐙 **GitHub Repo**: [github.com/aanxieee/75-PROBLEMS-BY-AANXIEE---AANYA-MITTAL-](https://github.com/aanxieee/75-PROBLEMS-BY-AANXIEE---AANYA-MITTAL-)
- 💼 **LinkedIn**: [aanya-mittal-aka-aanxiee](https://www.linkedin.com/in/aanya-mittal-aka-aanxiee/)
- 🌍 **Website**: [aanxiee.com](https://aanxiee.com)

---

## 📜 License

MIT — free to use, modify, and distribute.

---

*Day 04 / 75 — #75DayAIChallenge*  
*Challenge Start: 8th March 2025*  
*Code shipped. Every single day.*
