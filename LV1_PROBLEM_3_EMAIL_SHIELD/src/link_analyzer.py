"""URL extraction and risk checks performed without opening links."""

from __future__ import annotations

from dataclasses import dataclass, field

from src.domain_analyzer import analyze_domain
from src.utils import SHORTENER_DOMAINS, count_subdomains, has_encoded_segments, is_ip_hostname, safe_urlparse


@dataclass
class UrlAnalysis:
    url: str
    domain: str
    score: int = 0
    flags: list[str] = field(default_factory=list)
    root_domain: str = ""
    domain_flags: list[str] = field(default_factory=list)


def analyze_url(url: str) -> UrlAnalysis:
    parsed = safe_urlparse(url)
    hostname = (parsed.hostname or "").lower()
    result = UrlAnalysis(url=url, domain=hostname)

    if not hostname:
        result.score += 10
        result.flags.append("URL is malformed or missing a hostname")
        return result

    if is_ip_hostname(hostname):
        result.score += 30
        result.flags.append("IP-based URL")

    if len(url) > 120:
        result.score += 15
        result.flags.append("Very long URL")

    subdomain_count = count_subdomains(hostname)
    if subdomain_count >= 3:
        result.score += 15
        result.flags.append("Excessive subdomains")

    if has_encoded_segments(url):
        result.score += 15
        result.flags.append("Encoded or obfuscated URL")

    if hostname in SHORTENER_DOMAINS:
        result.score += 20
        result.flags.append("Known URL shortener")

    domain_analysis = analyze_domain(hostname)
    result.root_domain = domain_analysis.root_domain
    result.domain_flags.extend(domain_analysis.flags)
    result.score += domain_analysis.score

    return result


def analyze_urls(urls: list[str]) -> list[UrlAnalysis]:
    return [analyze_url(url) for url in urls]