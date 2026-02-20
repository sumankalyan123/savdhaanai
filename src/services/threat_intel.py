from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass, field
from datetime import UTC

import httpx
import structlog

from src.api.schemas.scan import EvidenceItem
from src.core.config import settings
from src.core.constants import THREAT_INTEL_PER_SOURCE_TIMEOUT, ThreatSource
from src.utils.url_parser import get_domain

logger = structlog.get_logger()


@dataclass
class ThreatCheckResult:
    source: ThreatSource
    is_threat: bool = False
    threat_type: str | None = None
    confidence: float = 0.0
    details: dict = field(default_factory=dict)
    response_time_ms: int = 0
    error: str | None = None


async def check_all_threats(
    urls: list[str],
    domains: list[str] | None = None,
) -> list[ThreatCheckResult]:
    """Run all threat intel checks in parallel. Graceful degradation on failures."""
    if not urls and not domains:
        return []

    if domains is None:
        domains = list({get_domain(url) for url in urls})

    tasks = []
    for url in urls:
        tasks.append(_check_google_safe_browsing(url))
        tasks.append(_check_phishtank(url))
        tasks.append(_check_urlhaus(url))

    for domain in domains:
        tasks.append(_check_whois(domain))

    results = await asyncio.gather(*tasks, return_exceptions=True)

    threat_results = []
    for result in results:
        if isinstance(result, ThreatCheckResult):
            threat_results.append(result)
        elif isinstance(result, Exception):
            await logger.awarning("threat_check_failed", error=str(result))

    return threat_results


def results_to_evidence(results: list[ThreatCheckResult]) -> list[EvidenceItem]:
    """Convert threat check results to evidence items for the scan response."""
    evidence = []
    for r in results:
        if r.error:
            continue
        evidence.append(
            EvidenceItem(
                source=r.source.value,
                detail=r.details.get("summary", f"Checked via {r.source.value}"),
                is_threat=r.is_threat,
                confidence=r.confidence,
            )
        )
    return evidence


async def _check_google_safe_browsing(url: str) -> ThreatCheckResult:
    """Check URL against Google Safe Browsing API v4."""
    start = time.perf_counter()
    result = ThreatCheckResult(source=ThreatSource.GOOGLE_SAFE_BROWSING)

    if not settings.GOOGLE_SAFE_BROWSING_KEY:
        result.details = {"summary": "Google Safe Browsing not configured"}
        return result

    try:
        async with httpx.AsyncClient(timeout=THREAT_INTEL_PER_SOURCE_TIMEOUT) as client:
            resp = await client.post(
                f"https://safebrowsing.googleapis.com/v4/threatMatches:find"
                f"?key={settings.GOOGLE_SAFE_BROWSING_KEY}",
                json={
                    "client": {"clientId": "savdhaan-ai", "clientVersion": "0.1.0"},
                    "threatInfo": {
                        "threatTypes": [
                            "MALWARE",
                            "SOCIAL_ENGINEERING",
                            "UNWANTED_SOFTWARE",
                            "POTENTIALLY_HARMFUL_APPLICATION",
                        ],
                        "platformTypes": ["ANY_PLATFORM"],
                        "threatEntryTypes": ["URL"],
                        "threatEntries": [{"url": url}],
                    },
                },
            )
            resp.raise_for_status()
            data = resp.json()

            if data.get("matches"):
                match = data["matches"][0]
                result.is_threat = True
                result.threat_type = match.get("threatType", "unknown")
                result.confidence = 0.95
                result.details = {
                    "summary": (
                        f"URL flagged as {match.get('threatType', 'threat')}"
                        " by Google Safe Browsing"
                    ),
                    "threat_type": match.get("threatType"),
                }
            else:
                result.details = {"summary": "URL not found in Google Safe Browsing database"}

    except Exception as e:
        result.error = str(e)
        await logger.awarning("google_safe_browsing_failed", url=url[:50], error=str(e))

    result.response_time_ms = round((time.perf_counter() - start) * 1000)
    return result


async def _check_phishtank(url: str) -> ThreatCheckResult:
    """Check URL against PhishTank database."""
    start = time.perf_counter()
    result = ThreatCheckResult(source=ThreatSource.PHISHTANK)

    if not settings.PHISHTANK_API_KEY:
        result.details = {"summary": "PhishTank not configured"}
        return result

    try:
        async with httpx.AsyncClient(timeout=THREAT_INTEL_PER_SOURCE_TIMEOUT) as client:
            resp = await client.post(
                "https://checkurl.phishtank.com/checkurl/",
                data={
                    "url": url,
                    "format": "json",
                    "app_key": settings.PHISHTANK_API_KEY,
                },
            )
            resp.raise_for_status()
            data = resp.json()
            results_data = data.get("results", {})

            if results_data.get("in_database") and results_data.get("valid"):
                result.is_threat = True
                result.threat_type = "phishing"
                result.confidence = 0.95 if results_data.get("verified") else 0.7
                result.details = {
                    "summary": "URL found in PhishTank phishing database",
                    "verified": results_data.get("verified", False),
                    "phish_id": results_data.get("phish_id"),
                }
            else:
                result.details = {"summary": "URL not found in PhishTank database"}

    except Exception as e:
        result.error = str(e)
        await logger.awarning("phishtank_failed", url=url[:50], error=str(e))

    result.response_time_ms = round((time.perf_counter() - start) * 1000)
    return result


async def _check_urlhaus(url: str) -> ThreatCheckResult:
    """Check URL against URLhaus malware URL database."""
    start = time.perf_counter()
    result = ThreatCheckResult(source=ThreatSource.URLHAUS)

    if not settings.URLHAUS_ENABLED:
        result.details = {"summary": "URLhaus not enabled"}
        return result

    try:
        async with httpx.AsyncClient(timeout=THREAT_INTEL_PER_SOURCE_TIMEOUT) as client:
            resp = await client.post(
                "https://urlhaus-api.abuse.ch/v1/url/",
                data={"url": url},
            )
            resp.raise_for_status()
            data = resp.json()

            if data.get("query_status") == "listed":
                result.is_threat = True
                result.threat_type = data.get("threat", "malware")
                result.confidence = 0.9
                result.details = {
                    "summary": (
                        f"URL listed in URLhaus as distributing {data.get('threat', 'malware')}"
                    ),
                    "threat": data.get("threat"),
                    "tags": data.get("tags"),
                }
            else:
                result.details = {"summary": "URL not found in URLhaus database"}

    except Exception as e:
        result.error = str(e)
        await logger.awarning("urlhaus_failed", url=url[:50], error=str(e))

    result.response_time_ms = round((time.perf_counter() - start) * 1000)
    return result


async def _check_whois(domain: str) -> ThreatCheckResult:
    """Check domain age via WHOIS — new domains are suspicious."""
    start = time.perf_counter()
    result = ThreatCheckResult(source=ThreatSource.WHOIS)

    try:
        import whois

        w = await asyncio.to_thread(whois.whois, domain)

        creation_date = w.creation_date
        if isinstance(creation_date, list):
            creation_date = creation_date[0]

        if creation_date:
            from datetime import datetime

            age_days = (datetime.now(tz=UTC) - creation_date.replace(tzinfo=UTC)).days

            if age_days < 7:
                result.is_threat = True
                result.threat_type = "new_domain"
                result.confidence = 0.6
                result.details = {
                    "summary": f"Domain registered {age_days} days ago — very new, high risk",
                    "domain_age_days": age_days,
                    "registrar": w.registrar,
                }
            elif age_days < 30:
                result.is_threat = True
                result.threat_type = "new_domain"
                result.confidence = 0.3
                result.details = {
                    "summary": f"Domain registered {age_days} days ago — relatively new",
                    "domain_age_days": age_days,
                    "registrar": w.registrar,
                }
            else:
                result.details = {
                    "summary": f"Domain registered {age_days} days ago",
                    "domain_age_days": age_days,
                    "registrar": w.registrar,
                }
        else:
            result.details = {"summary": "WHOIS creation date not available"}

    except Exception as e:
        result.error = str(e)
        await logger.awarning("whois_failed", domain=domain, error=str(e))

    result.response_time_ms = round((time.perf_counter() - start) * 1000)
    return result
