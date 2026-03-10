"""Domain analysis heuristics for offline phishing detection."""

from __future__ import annotations

from dataclasses import dataclass, field

import tldextract

from src.utils import has_unusual_domain_chars, looks_like_typosquat

OFFLINE_EXTRACT = tldextract.TLDExtract(suffix_list_urls=None)


@dataclass
class DomainAnalysis:
    domain: str
    root_domain: str
    score: int = 0
    flags: list[str] = field(default_factory=list)
    matched_brand: str = ""


def extract_root_domain(domain: str) -> str:
    extracted = OFFLINE_EXTRACT(domain or "")
    if not extracted.domain or not extracted.suffix:
        return (domain or "").lower()
    return f"{extracted.domain}.{extracted.suffix}".lower()


def analyze_domain(domain: str) -> DomainAnalysis:
    domain = (domain or "").lower().strip(".")
    root_domain = extract_root_domain(domain)
    extracted = OFFLINE_EXTRACT(root_domain)
    label = extracted.domain or root_domain.split(".")[0]

    result = DomainAnalysis(domain=domain, root_domain=root_domain)

    if any(char.isdigit() for char in label):
        result.score += 10
        result.flags.append("Domain contains numeric characters")

    if has_unusual_domain_chars(domain):
        result.score += 10
        result.flags.append("Domain contains unusual characters")

    hyphen_count = root_domain.count("-")
    if hyphen_count >= 2:
        result.score += 10
        result.flags.append("Domain contains multiple hyphens")

    is_typosquat, brand = looks_like_typosquat(label)
    if is_typosquat:
        result.score += 30
        result.matched_brand = brand
        result.flags.append(f"Possible typosquatting of '{brand}'")

    return result