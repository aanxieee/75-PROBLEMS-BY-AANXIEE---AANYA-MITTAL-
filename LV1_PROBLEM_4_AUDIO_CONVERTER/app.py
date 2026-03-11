"""
🎧 Audio → Hindi Translator
Day 04 / 75 — Aanya's 75-Day AI Challenge
Stack: OpenAI Whisper (local STT) + googletrans (Hindi translation)
"""

import os
import tempfile
import streamlit as st
from pathlib import Path

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Audio → Hindi Translator",
    page_icon="🎧",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=Noto+Serif+Devanagari:wght@400;700&family=Space+Grotesk:wght@300;400;600;700&display=swap');

:root {
    --bg: #0d0f12;
    --surface: #161a20;
    --border: #272c35;
    --accent: #e8c547;
    --accent2: #4ecdc4;
    --text: #e2e4e9;
    --muted: #6b7280;
}

html, body, [class*="css"] {
    font-family: 'Space Grotesk', sans-serif;
    background-color: var(--bg) !important;
    color: var(--text) !important;
}
.stApp { background-color: var(--bg) !important; }

.main-title {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 2.4rem;
    font-weight: 600;
    letter-spacing: -0.02em;
    color: var(--accent);
    line-height: 1.1;
    margin-bottom: 0.2rem;
}
.sub-title {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.85rem;
    color: var(--muted);
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin-bottom: 2rem;
}
.card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 1.4rem 1.6rem;
    margin-bottom: 1.2rem;
}
.card-title {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.7rem;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: var(--accent);
    margin-bottom: 0.8rem;
}
.transcript-text {
    font-size: 1rem;
    line-height: 1.75;
    color: var(--text);
    white-space: pre-wrap;
}
.hindi-text {
    font-family: 'Noto Serif Devanagari', serif;
    font-size: 1.25rem;
    line-height: 2.1;
    color: #f0e6ff;
    white-space: pre-wrap;
}
.lang-badge {
    background: rgba(232,197,71,0.15);
    border: 1px solid var(--accent);
    color: var(--accent);
    border-radius: 4px;
    padding: 0.3rem 0.9rem;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.85rem;
    font-weight: 600;
    display: inline-block;
}
.step-indicator {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.72rem;
    color: var(--muted);
    letter-spacing: 0.08em;
}
.pipeline-flow {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    flex-wrap: wrap;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.72rem;
    color: var(--muted);
    margin-bottom: 1.5rem;
}
.pipeline-step { color: var(--accent2); }
.pipeline-arrow { color: var(--border); }

.stProgress > div > div { background-color: var(--accent) !important; }
div[data-testid="stFileUploader"] {
    border: 1px dashed var(--border) !important;
    border-radius: 8px !important;
    background: var(--surface) !important;
}
.stSelectbox > div > div, .stButton > button {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    color: var(--text) !important;
    border-radius: 6px !important;
}
.stButton > button:hover {
    border-color: var(--accent) !important;
    color: var(--accent) !important;
}
.stSidebar {
    background: var(--surface) !important;
    border-right: 1px solid var(--border) !important;
}
hr { border-color: var(--border) !important; }
</style>
""", unsafe_allow_html=True)


# ── Cached model loader ────────────────────────────────────────────────────────
@st.cache_resource(show_spinner=False)
def load_whisper_model(model_size: str):
    import whisper
    return whisper.load_model(model_size)


# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown('<div class="main-title">🎧 Audio → हिंदी</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Speech-to-text · Auto language detection · Hindi translation</div>', unsafe_allow_html=True)

st.markdown("""
<div class="pipeline-flow">
  <span class="pipeline-step">AUDIO UPLOAD</span>
  <span class="pipeline-arrow">──▶</span>
  <span class="pipeline-step">WHISPER STT</span>
  <span class="pipeline-arrow">──▶</span>
  <span class="pipeline-step">LANG DETECT</span>
  <span class="pipeline-arrow">──▶</span>
  <span class="pipeline-step">→ हिंदी</span>
  <span class="pipeline-arrow">──▶</span>
  <span class="pipeline-step">DOWNLOAD</span>
</div>
""", unsafe_allow_html=True)


# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ Settings")
    st.markdown("---")

    model_size = st.selectbox(
        "Whisper Model Size",
        options=["tiny", "base", "small"],
        index=0,
        help="tiny = fastest (recommended for Streamlit Cloud). base = better accuracy."
    )

    st.markdown("""
    | Model | Size | Speed |
    |-------|------|-------|
    | tiny  | 39 MB | fastest ⚡ |
    | base  | 74 MB | fast |
    | small | 244 MB | moderate |
    """)

    st.markdown("---")
    st.markdown("### 🌐 How It Works")
    st.markdown("""
    <div style="font-size:0.82rem; color:#6b7280; line-height:1.7;">
    1️⃣ Upload any audio file<br>
    2️⃣ Whisper transcribes it (99 languages)<br>
    3️⃣ Language auto-detected<br>
    4️⃣ Translated to Hindi via Google Translate<br>
    5️⃣ Download transcript + translation
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 🛠️ Stack")
    st.markdown("""
    <div style="font-size:0.82rem; color:#6b7280; line-height:1.7;">
    🎙️ <b>OpenAI Whisper</b> — local STT<br>
    🌐 <b>googletrans</b> — Hindi translation<br>
    🖥️ <b>Streamlit</b> — UI
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("""
    <div style="font-size:0.75rem; color:#4b5563; text-align:center;">
    Day 04 / 75 · #75DayAIChallenge<br>
    <a href="https://github.com/aanxieee/75-day-ai-challenge" style="color:#e8c547;">github.com/aanxieee</a>
    </div>
    """, unsafe_allow_html=True)


# ── Main layout ────────────────────────────────────────────────────────────────
col_upload, col_results = st.columns([1, 1.6], gap="large")

with col_upload:
    st.markdown("### 📂 Upload Audio")

    uploaded_file = st.file_uploader(
        "Drag & drop or browse",
        type=["wav", "mp3", "m4a", "ogg", "flac"],
        label_visibility="collapsed"
    )

    if uploaded_file:
        st.audio(uploaded_file, format=f"audio/{uploaded_file.name.split('.')[-1]}")
        st.markdown(f"""
        <div class="card" style="margin-top:0.8rem;">
            <div style="font-family:'IBM Plex Mono',monospace; font-size:0.75rem; color:#6b7280;">
                📄 {uploaded_file.name}<br>
                💾 {uploaded_file.size / 1024:.1f} KB
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    process_btn = st.button(
        "▶  Translate to Hindi",
        disabled=uploaded_file is None,
        use_container_width=True,
    )

    if not uploaded_file:
        st.markdown("""
        <div style="text-align:center; color:#6b7280; font-size:0.82rem; margin-top:1rem;">
        Supported: .wav · .mp3 · .m4a · .ogg · .flac
        </div>
        """, unsafe_allow_html=True)


# ── Processing ─────────────────────────────────────────────────────────────────
with col_results:
    if process_btn and uploaded_file is not None:

        suffix = Path(uploaded_file.name).suffix
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(uploaded_file.read())
            tmp_path = tmp.name

        try:
            progress = st.progress(0, text="Starting…")
            status   = st.empty()

            # Step 1 — Load Whisper
            status.markdown('<div class="step-indicator">STEP 1/3 · Loading Whisper model…</div>', unsafe_allow_html=True)
            model = load_whisper_model(model_size)
            progress.progress(20, text="Whisper ready")

            # Step 2 — Transcribe
            status.markdown('<div class="step-indicator">STEP 2/3 · Transcribing audio…</div>', unsafe_allow_html=True)
            result      = model.transcribe(tmp_path)
            transcript  = result["text"].strip()
            detected    = result.get("language", "unknown")
            progress.progress(60, text="Transcription done")

            # Step 3 — Translate to Hindi
            status.markdown('<div class="step-indicator">STEP 3/3 · Translating to Hindi…</div>', unsafe_allow_html=True)
            from googletrans import Translator, LANGUAGES
            translator  = Translator()
            hindi_text  = translator.translate(transcript, dest="hi").text
            lang_name   = LANGUAGES.get(detected, detected).title()
            progress.progress(100, text="Done ✓")
            status.empty()
            progress.empty()

            # ── Results ────────────────────────────────────────────────────────

            # Language badge
            st.markdown(f"""
            <div class="card">
                <div class="card-title">🌐 Detected Language</div>
                <span class="lang-badge">{lang_name}</span>
                <span style="font-family:'IBM Plex Mono',monospace; font-size:0.75rem;
                             color:#6b7280; margin-left:0.7rem;">code: {detected}</span>
            </div>
            """, unsafe_allow_html=True)

            # Transcript
            st.markdown(f"""
            <div class="card">
                <div class="card-title">📝 Original Transcript</div>
                <div class="transcript-text">{transcript}</div>
            </div>
            """, unsafe_allow_html=True)

            # Hindi translation
            st.markdown(f"""
            <div class="card">
                <div class="card-title">🇮🇳 Hindi Translation · हिंदी अनुवाद</div>
                <div class="hindi-text">{hindi_text}</div>
            </div>
            """, unsafe_allow_html=True)

            # Download buttons
            st.markdown("### 💾 Download")
            combined = (
                f"=== ORIGINAL TRANSCRIPT ({lang_name}) ===\n\n{transcript}"
                f"\n\n=== HINDI TRANSLATION · हिंदी अनुवाद ===\n\n{hindi_text}"
            )
            col_dl1, col_dl2 = st.columns(2)
            with col_dl1:
                st.download_button(
                    "⬇ Transcript (.txt)",
                    data=transcript,
                    file_name="transcript.txt",
                    mime="text/plain",
                    use_container_width=True,
                )
            with col_dl2:
                st.download_button(
                    "⬇ Full Translation (.txt)",
                    data=combined,
                    file_name="translation_hindi.txt",
                    mime="text/plain",
                    use_container_width=True,
                )

        except Exception as e:
            st.error(f"❌ Processing failed: {str(e)}")
            st.markdown("""
            **Troubleshooting:**
            - Make sure `ffmpeg` is installed on your system
            - Try a smaller Whisper model (`tiny`)
            - Check that the audio file is not corrupted
            """)
        finally:
            os.unlink(tmp_path)

    elif not process_btn:
        st.markdown("""
        <div style="display:flex; flex-direction:column; align-items:center;
                    justify-content:center; height:400px; color:#6b7280; text-align:center;">
            <div style="font-size:3rem; margin-bottom:1rem;">🎙️</div>
            <div style="font-family:'IBM Plex Mono',monospace; font-size:0.85rem; letter-spacing:0.1em;">
                UPLOAD AUDIO TO BEGIN
            </div>
            <div style="font-size:0.78rem; margin-top:0.5rem; color:#4b5563;">
                Any language → हिंदी
            </div>
        </div>
        """, unsafe_allow_html=True)
