"""Utility helpers for offline email analysis."""

from __future__ import annotations

import ipaddress
import re
from difflib import SequenceMatcher
from email.utils import parseaddr
from html import unescape
from typing import Iterable, List
from urllib.parse import unquote, urlparse

from bs4 import BeautifulSoup

SAFE_BRANDS = {
    "paypal",
    "microsoft",
    "google",
    "apple",
    "amazon",
    "outlook",
    "office365",
    "bankofamerica",
    "dropbox",
    "docusign",
}

SHORTENER_DOMAINS = {
    "bit.ly",
    "tinyurl.com",
    "t.co",
    "goo.gl",
    "ow.ly",
    "is.gd",
    "buff.ly",
    "tiny.one",
    "rebrand.ly",
    "cutt.ly",
}

HIGH_RISK_EXTENSIONS = {
    ".exe",
    ".scr",
    ".js",
    ".vbs",
    ".docm",
    ".xlsm",
    ".bat",
}

URL_PATTERN = re.compile(r"(?i)\b((?:https?://|www\.)[^\s<>'\"]+)")
EMAIL_PATTERN = re.compile(r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}", re.IGNORECASE)


def extract_urls(text: str) -> List[str]:
    if not text:
        return []
    seen = []
    for match in URL_PATTERN.findall(text):
        cleaned = match.rstrip(").,>;\"")
        if cleaned not in seen:
            seen.append(cleaned)
    return seen


def html_to_text(html: str) -> str:
    if not html:
        return ""
    soup = BeautifulSoup(html, "html.parser")
    return unescape(soup.get_text(" ", strip=True))


def normalize_email(value: str) -> str:
    _, email_address = parseaddr(value or "")
    return email_address.lower().strip()


def extract_email_domain(value: str) -> str:
    email_address = normalize_email(value)
    if "@" not in email_address:
        return ""
    return email_address.rsplit("@", 1)[-1]


def deduplicate(items: Iterable[str]) -> List[str]:
    results = []
    for item in items:
        if item and item not in results:
            results.append(item)
    return results


def is_ip_hostname(hostname: str) -> bool:
    if not hostname:
        return False
    candidate = hostname.strip("[]")
    try:
        ipaddress.ip_address(candidate)
        return True
    except ValueError:
        return False


def has_encoded_segments(url: str) -> bool:
    return "%" in url or unquote(url) != url


def count_subdomains(hostname: str) -> int:
    if not hostname:
        return 0
    parts = [part for part in hostname.split(".") if part]
    return max(len(parts) - 2, 0)


def has_unusual_domain_chars(domain: str) -> bool:
    return bool(re.search(r"[^a-z0-9.-]", domain.lower()))


def similarity_ratio(left: str, right: str) -> float:
    return SequenceMatcher(None, left.lower(), right.lower()).ratio()


def levenshtein_distance(left: str, right: str) -> int:
    if left == right:
        return 0
    if not left:
        return len(right)
    if not right:
        return len(left)

    previous_row = list(range(len(right) + 1))
    for i, left_char in enumerate(left, start=1):
        current_row = [i]
        for j, right_char in enumerate(right, start=1):
            insertions = previous_row[j] + 1
            deletions = current_row[j - 1] + 1
            substitutions = previous_row[j - 1] + (left_char != right_char)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    return previous_row[-1]


def looks_like_typosquat(domain_label: str) -> tuple[bool, str]:
    normalized = re.sub(r"[^a-z0-9]", "", domain_label.lower())
    if not normalized:
        return False, ""

    for brand in SAFE_BRANDS:
        distance = levenshtein_distance(normalized, brand)
        ratio = similarity_ratio(normalized, brand)
        contains_brand = brand in normalized and normalized != brand
        if contains_brand or distance == 1 or ratio >= 0.88:
            return True, brand
    return False, ""


def safe_urlparse(url: str):
    candidate = url.strip()
    if candidate.startswith("www."):
        candidate = f"http://{candidate}"
    return urlparse(candidate)


def find_possible_email_addresses(text: str) -> List[str]:
    return deduplicate(match.group(0) for match in EMAIL_PATTERN.finditer(text or ""))