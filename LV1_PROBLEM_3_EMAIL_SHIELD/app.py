"""Streamlit interface for offline email analysis."""

from __future__ import annotations

import tempfile
from pathlib import Path

import pandas as pd
import streamlit as st

from src.email_parser import ParsedEmail, parse_pasted_email, parse_uploaded_email
from src.header_analyzer import analyze_headers
from src.link_analyzer import analyze_urls
from src.risk_engine import analyze_attachments, build_risk_report


st.set_page_config(page_title="EmailShield Analyzer", page_icon="🛡️", layout="wide")


def _save_temp_file(file_name: str, content: bytes) -> str:
    suffix = Path(file_name).suffix
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as handle:
        handle.write(content)
        return handle.name


def _display_email_summary(parsed_email: ParsedEmail) -> None:
    col1, col2 = st.columns(2)
    with col1:
        st.text_input("Sender", parsed_email.sender or "Unknown", disabled=True)
        st.text_input("Reply-To", parsed_email.reply_to or "Not present", disabled=True)
    with col2:
        st.text_input("Subject", parsed_email.subject or "No subject", disabled=True)
        st.text_input("Attachments", ", ".join(parsed_email.attachment_names) or "None", disabled=True)

    st.subheader("Body Text")
    st.text_area("Extracted body", parsed_email.body_text or "No body content extracted.", height=220, disabled=True)


def _display_link_results(url_results) -> None:
    st.subheader("Extracted URLs")
    if not url_results:
        st.info("No URLs were detected in the email body or headers.")
        return

    url_frame = pd.DataFrame(
        [
            {
                "URL": result.url,
                "Domain": result.domain,
                "Root Domain": result.root_domain,
                "Score": result.score,
                "Flags": "; ".join(result.flags + result.domain_flags) or "None",
            }
            for result in url_results
        ]
    )
    st.dataframe(url_frame, use_container_width=True)


def _display_attachment_results(attachment_results) -> None:
    st.subheader("Attachment Analysis")
    if not attachment_results:
        st.info("No attachments were found.")
        return

    attachment_frame = pd.DataFrame(
        [
            {
                "Attachment": result.name,
                "Score": result.score,
                "Flags": "; ".join(result.flags) or "None",
            }
            for result in attachment_results
        ]
    )
    st.dataframe(attachment_frame, use_container_width=True)


def _display_headers(parsed_email: ParsedEmail, header_warnings: list[str]) -> None:
    st.subheader("Header Warnings")
    if header_warnings:
        for warning in header_warnings:
            st.warning(warning)
    else:
        st.success("No obvious header anomalies were detected.")

    with st.expander("Raw Headers"):
        if parsed_email.headers:
            st.json(parsed_email.headers)
        else:
            st.write("No structured headers available.")


def main() -> None:
    st.title("EmailShield Analyzer")
    st.caption("Local offline phishing analysis for .eml, .msg, and pasted email text. Links and attachments are never opened.")

    st.sidebar.header("Usage")
    st.sidebar.code("pip install -r requirements.txt\nstreamlit run app.py")
    st.sidebar.info("This tool performs static analysis only. It does not call external APIs or open links.")
    st.sidebar.caption("Sample mail files are available in ./data/emails and placeholder attachments in ./data/attachments.")

    upload_col, paste_col = st.columns([1, 1])

    with upload_col:
        uploaded_file = st.file_uploader("Upload Email File", type=["eml", "msg"])
    with paste_col:
        pasted_text = st.text_area("Or paste raw email text", height=180)

    analyze = st.button("Analyze", type="primary")

    if not analyze:
        st.info("Choose a file or paste an email, then run the analyzer.")
        return

    if not uploaded_file and not pasted_text.strip():
        st.error("Provide either an uploaded email file or pasted email text.")
        return

    try:
        if uploaded_file:
            file_bytes = uploaded_file.getvalue()
            temp_path = _save_temp_file(uploaded_file.name, file_bytes) if uploaded_file.name.lower().endswith(".msg") else None
            parsed_email = parse_uploaded_email(uploaded_file.name, file_bytes, temp_path=temp_path)
        else:
            parsed_email = parse_pasted_email(pasted_text)
    except Exception as exc:
        st.error(f"Unable to parse email: {exc}")
        return

    url_results = analyze_urls(parsed_email.urls)
    header_result = analyze_headers(parsed_email.headers, parsed_email.sender, parsed_email.reply_to)
    attachment_results = analyze_attachments(parsed_email.attachment_names)
    report = build_risk_report(url_results, header_result, attachment_results)

    st.subheader("Threat Report Panel")
    verdict_color = {
        "SAFE": "green",
        "SUSPICIOUS": "orange",
        "HIGH RISK": "red",
    }[report.verdict]
    st.markdown(
        f"""
        <div style="padding: 1rem; border-radius: 0.75rem; border: 1px solid #d1d5db; margin-bottom: 1rem;">
            <div style="font-size: 0.95rem; color: #4b5563;">Final Risk Score</div>
            <div style="font-size: 2rem; font-weight: 700;">{report.total_score}</div>
            <div style="font-size: 1.1rem; font-weight: 600; color: {verdict_color};">Verdict: {report.verdict}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    _display_email_summary(parsed_email)
    _display_link_results(url_results)
    _display_attachment_results(attachment_results)
    _display_headers(parsed_email, header_result.warnings)

    st.subheader("Findings")
    if report.findings:
        findings_frame = pd.DataFrame({"Finding": report.findings})
        st.dataframe(findings_frame, use_container_width=True)
    else:
        st.success("No suspicious indicators were triggered by the current scoring rules.")


if __name__ == "__main__":
    main()