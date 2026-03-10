"""Risk scoring engine for EmailShield Analyzer."""

from __future__ import annotations

from dataclasses import dataclass, field

from src.header_analyzer import HeaderAnalysis
from src.link_analyzer import UrlAnalysis
from src.utils import HIGH_RISK_EXTENSIONS


@dataclass
class AttachmentAnalysis:
    name: str
    score: int = 0
    flags: list[str] = field(default_factory=list)


@dataclass
class RiskReport:
    total_score: int
    verdict: str
    findings: list[str]
    attachment_results: list[AttachmentAnalysis]


def analyze_attachments(attachments: list[str]) -> list[AttachmentAnalysis]:
    results = []
    for attachment in attachments:
        lowered = attachment.lower()
        analysis = AttachmentAnalysis(name=attachment)
        for extension in HIGH_RISK_EXTENSIONS:
            if lowered.endswith(extension):
                analysis.score += 40
                analysis.flags.append(f"Dangerous attachment type: {extension}")
                break
        results.append(analysis)
    return results


def verdict_for_score(score: int) -> str:
    if score < 30:
        return "SAFE"
    if score < 60:
        return "SUSPICIOUS"
    return "HIGH RISK"


def build_risk_report(
    url_results: list[UrlAnalysis],
    header_result: HeaderAnalysis,
    attachment_results: list[AttachmentAnalysis],
) -> RiskReport:
    findings: list[str] = []
    total_score = header_result.score
    findings.extend(header_result.warnings)

    for url_result in url_results:
        total_score += url_result.score
        findings.extend([f"{url_result.url}: {flag}" for flag in url_result.flags])
        findings.extend([f"{url_result.domain}: {flag}" for flag in url_result.domain_flags])

    for attachment_result in attachment_results:
        total_score += attachment_result.score
        findings.extend([f"{attachment_result.name}: {flag}" for flag in attachment_result.flags])

    verdict = verdict_for_score(total_score)
    return RiskReport(
        total_score=total_score,
        verdict=verdict,
        findings=findings,
        attachment_results=attachment_results,
    )