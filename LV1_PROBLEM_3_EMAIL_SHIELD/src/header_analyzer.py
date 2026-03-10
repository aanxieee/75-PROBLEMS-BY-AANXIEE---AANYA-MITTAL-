"""Email header heuristics for suspicious routing and auth failures."""

from __future__ import annotations

from dataclasses import dataclass, field

from src.utils import extract_email_domain, normalize_email


@dataclass
class HeaderAnalysis:
    score: int = 0
    warnings: list[str] = field(default_factory=list)


def _header_values(headers: dict[str, list[str] | str], key: str) -> list[str]:
    value = headers.get(key, [])
    if isinstance(value, list):
        return [item for item in value if item]
    if value:
        return [value]
    return []


def analyze_headers(headers: dict[str, list[str] | str], sender: str, reply_to: str) -> HeaderAnalysis:
    analysis = HeaderAnalysis()
    sender_email = normalize_email(sender)
    reply_to_email = normalize_email(reply_to)

    if sender_email and reply_to_email and sender_email != reply_to_email:
        analysis.score += 20
        analysis.warnings.append("Sender and Reply-To addresses do not match")
    elif extract_email_domain(sender) and extract_email_domain(reply_to) and extract_email_domain(sender) != extract_email_domain(reply_to):
        analysis.score += 20
        analysis.warnings.append("Sender and Reply-To domains do not match")

    auth_headers = " ".join(_header_values(headers, "Authentication-Results") + _header_values(headers, "authentication-results")).lower()
    spf_headers = " ".join(_header_values(headers, "Received-SPF") + _header_values(headers, "received-spf")).lower()

    if "spf=fail" in auth_headers or "spf fail" in spf_headers or "softfail" in spf_headers:
        analysis.score += 20
        analysis.warnings.append("SPF failure indicator detected")

    if "dkim=fail" in auth_headers or "dkim=temperror" in auth_headers or "dkim=permerror" in auth_headers:
        analysis.score += 20
        analysis.warnings.append("DKIM failure indicator detected")

    received_chain = _header_values(headers, "Received") + _header_values(headers, "received")
    if len(received_chain) >= 6:
        analysis.score += 10
        analysis.warnings.append("Long mail relay chain detected")

    suspicious_relays = [entry for entry in received_chain if "unknown" in entry.lower() or "localhost" in entry.lower()]
    if suspicious_relays:
        analysis.score += 10
        analysis.warnings.append("Suspicious relay hop found in Received headers")

    return analysis