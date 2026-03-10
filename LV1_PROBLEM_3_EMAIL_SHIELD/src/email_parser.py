"""Parsing helpers for .eml, .msg, and pasted email text."""

from __future__ import annotations

from dataclasses import dataclass, field
from email import policy
from email.parser import BytesParser, Parser
from email.utils import parseaddr
from typing import Any

from src.utils import deduplicate, extract_urls, find_possible_email_addresses, html_to_text

try:
    import extract_msg
except ImportError:  # pragma: no cover - dependency is provided in requirements.txt.
    extract_msg = None


@dataclass
class ParsedEmail:
    sender: str = ""
    reply_to: str = ""
    subject: str = ""
    body_text: str = ""
    urls: list[str] = field(default_factory=list)
    attachment_names: list[str] = field(default_factory=list)
    headers: dict[str, list[str] | str] = field(default_factory=dict)


def _headers_to_dict(message) -> dict[str, list[str] | str]:
    headers: dict[str, list[str]] = {}
    for key, value in message.items():
        headers.setdefault(key, []).append(value)
    return headers


def _pick_body_from_message(message) -> str:
    body_chunks: list[str] = []
    if message.is_multipart():
        for part in message.walk():
            content_disposition = part.get_content_disposition()
            content_type = part.get_content_type()
            if content_disposition == "attachment":
                continue
            try:
                payload = part.get_content()
            except Exception:
                continue
            if not payload:
                continue
            if content_type == "text/plain":
                body_chunks.append(str(payload))
            elif content_type == "text/html":
                body_chunks.append(html_to_text(str(payload)))
    else:
        try:
            payload = message.get_content()
        except Exception:
            payload = ""
        if message.get_content_type() == "text/html":
            body_chunks.append(html_to_text(str(payload)))
        else:
            body_chunks.append(str(payload))

    return "\n".join(chunk.strip() for chunk in body_chunks if chunk and chunk.strip())


def _pick_attachments_from_message(message) -> list[str]:
    attachments: list[str] = []
    for part in message.walk():
        if part.get_content_disposition() == "attachment":
            filename = part.get_filename()
            if filename:
                attachments.append(filename)
    return attachments


def _sender_from_headers(message, key: str) -> str:
    value = message.get(key, "")
    display_name, address = parseaddr(value)
    return f"{display_name} <{address}>" if display_name and address else value


def parse_eml_bytes(file_bytes: bytes) -> ParsedEmail:
    message = BytesParser(policy=policy.default).parsebytes(file_bytes)
    body_text = _pick_body_from_message(message)

    parsed = ParsedEmail(
        sender=_sender_from_headers(message, "From"),
        reply_to=_sender_from_headers(message, "Reply-To"),
        subject=message.get("Subject", ""),
        body_text=body_text,
        attachment_names=_pick_attachments_from_message(message),
        headers=_headers_to_dict(message),
    )
    parsed.urls = deduplicate(extract_urls(body_text) + extract_urls(str(message)))
    return parsed


def parse_msg_file(file_path: str) -> ParsedEmail:
    if extract_msg is None:
        raise RuntimeError("MSG parsing requires the extract-msg dependency.")

    message = extract_msg.Message(file_path)
    sender = message.sender or ""
    reply_to = message.header.get("reply-to", "") if getattr(message, "header", None) else ""
    subject = message.subject or ""
    body_text = message.body or html_to_text(getattr(message, "htmlBody", ""))
    attachment_names = [attachment.longFilename or attachment.shortFilename for attachment in message.attachments]
    headers = dict(getattr(message, "header", {}) or {})

    parsed = ParsedEmail(
        sender=sender,
        reply_to=reply_to,
        subject=subject,
        body_text=body_text,
        attachment_names=deduplicate(name for name in attachment_names if name),
        headers=headers,
    )
    parsed.urls = deduplicate(extract_urls(body_text) + extract_urls(str(headers)))
    return parsed


def parse_pasted_email(raw_text: str) -> ParsedEmail:
    text = raw_text or ""
    parsed_message = Parser(policy=policy.default).parsestr(text)
    has_structured_headers = bool(parsed_message.keys()) and any(key.lower() == "from" for key in parsed_message.keys())

    if has_structured_headers:
        return parse_eml_bytes(text.encode("utf-8", errors="ignore"))

    reply_candidates = []
    sender_candidates = find_possible_email_addresses(text)
    lowered_lines = text.splitlines()
    for line in lowered_lines:
        lower = line.lower()
        if lower.startswith("reply-to:"):
            reply_candidates.extend(find_possible_email_addresses(line))

    return ParsedEmail(
        sender=sender_candidates[0] if sender_candidates else "",
        reply_to=reply_candidates[0] if reply_candidates else "",
        subject="Pasted Email Text",
        body_text=text,
        urls=extract_urls(text),
        attachment_names=[],
        headers={},
    )


def parse_uploaded_email(file_name: str, file_bytes: bytes, temp_path: str | None = None) -> ParsedEmail:
    file_name = file_name.lower()
    if file_name.endswith(".eml"):
        return parse_eml_bytes(file_bytes)
    if file_name.endswith(".msg"):
        if not temp_path:
            raise RuntimeError("A temporary file path is required for MSG analysis.")
        return parse_msg_file(temp_path)
    raise ValueError("Unsupported file type. Upload an .eml or .msg file.")