# Savdhaan AI — Threat Intelligence Integration

> Last updated: 2026-02-20

---

## Overview

Savdhaan AI aggregates multiple threat intelligence sources to provide **evidence-grounded**
scam detection. No single source is authoritative — the system combines signals from all
available sources to build a confidence picture.

**Key principle**: Every source is optional. If any source is down, the scan still completes
with remaining sources + LLM analysis. Partial results > no results.

---

## Source Matrix

| Source | What It Checks | Free Tier | Rate Limit | Latency (p95) | Priority |
|--------|---------------|-----------|------------|---------------|----------|
| **Google Safe Browsing** | URL reputation (malware, social engineering, unwanted software) | 10K lookups/day | 10K/day | ~100ms | P0 (MVP 1) |
| **PhishTank** | Known phishing URLs (community-verified) | Yes | 30 req/min | ~200ms | P0 (MVP 1) |
| **URLhaus** | Malware distribution URLs (abuse.ch) | Yes | No hard limit | ~150ms | P0 (MVP 1) |
| **Spamhaus** | Domain/IP blocklists (SBL, DBL, XBL) | DQS free tier | DNS-based | ~50ms | P0 (MVP 1) |
| **WHOIS / RDAP** | Domain age, registrar, registration details | Yes (RDAP) | Varies | ~500ms | P0 (MVP 1) |
| **VirusTotal** | Multi-engine URL/file scanning | 4 req/min (free) | 4/min, 500/day | ~1000ms | P1 (Post-MVP) |
| **AbuseIPDB** | IP reputation and abuse reports | 1K checks/day | 1K/day | ~200ms | P2 (Post-MVP) |

---

## Integration Details

### Google Safe Browsing API v4

**What**: Google's URL reputation service. Checks URLs against continuously updated lists
of unsafe web resources (malware, social engineering, unwanted software, potentially harmful applications).

**How**:
```
POST https://safebrowsing.googleapis.com/v4/threatMatches:find?key=<API_KEY>

Body: {
  "client": { "clientId": "savdhaan-ai", "clientVersion": "1.0.0" },
  "threatInfo": {
    "threatTypes": ["MALWARE", "SOCIAL_ENGINEERING", "UNWANTED_SOFTWARE", "POTENTIALLY_HARMFUL_APPLICATION"],
    "platformTypes": ["ANY_PLATFORM"],
    "threatEntryTypes": ["URL"],
    "threatEntries": [
      { "url": "http://malicious-site.com/phish" }
    ]
  }
}
```

**Response parsing**:
- Empty `matches` → URL is clean
- Non-empty `matches` → URL flagged, extract `threatType` for classification

**Env var**: `GOOGLE_SAFE_BROWSING_KEY`

---

### PhishTank API

**What**: Community-driven phishing URL verification database. Users submit and verify
phishing sites. Large, frequently updated database.

**How**:
```
POST https://checkurl.phishtank.com/checkurl/

Body (form-encoded):
  url=http://suspicious-site.com
  format=json
  app_key=<API_KEY>
```

**Response parsing**:
- `results.in_database` → boolean, whether URL is known
- `results.verified` → boolean, whether community has verified it as phishing
- `results.phish_id` → reference ID for the phishing entry

**Env var**: `PHISHTANK_API_KEY`

---

### URLhaus (abuse.ch)

**What**: Tracks URLs that distribute malware. Operated by abuse.ch, a non-profit security project.

**How**:
```
POST https://urlhaus-api.abuse.ch/v1/url/

Body (form-encoded):
  url=http://malware-host.com/payload
```

**Response parsing**:
- `query_status: "ok"` + `url_status: "online"` → active malware URL
- `threat` → malware type (e.g., "malware_download")
- `tags` → additional classification tags

**Env var**: None (free, no key required)

---

### Spamhaus DQS (DNS Query Service)

**What**: Industry-standard blocklists for spam, phishing, and malware domains/IPs.
Uses DNS queries (fast, lightweight).

**Lists checked**:
- **SBL** (Spamhaus Block List): Known spam sources
- **XBL** (Exploits Block List): Compromised machines
- **DBL** (Domain Block List): Domains used for spam/phishing/malware

**How** (DNS-based lookup):
```python
# For domain lookup against DBL
import dns.resolver

query = f"example.com.{dqs_key}.dbl.dq.spamhaus.net"
answers = dns.resolver.resolve(query, 'A')
# 127.0.1.2 = spam domain
# 127.0.1.4 = phishing domain
# 127.0.1.5 = malware domain
# NXDOMAIN = clean
```

**Env var**: `SPAMHAUS_DQS_KEY`

---

### WHOIS / RDAP Domain Lookup

**What**: Domain registration data — critically, the **domain age**. Newly registered
domains (< 30 days) used in messages are a strong scam indicator.

**How**:
```python
import whois

result = whois.whois("suspicious-domain.com")
creation_date = result.creation_date
domain_age_days = (datetime.now() - creation_date).days
```

**Key signals**:
| Domain Age | Risk Signal |
|-----------|-------------|
| < 7 days | Very high risk — likely created for this scam |
| 7-30 days | High risk — very new domain |
| 30-90 days | Moderate risk — still relatively new |
| 90-365 days | Low risk signal from age alone |
| > 365 days | Age is not a risk factor |

**Additional signals**:
- Anonymous/privacy registrar → moderate risk signal
- Registrar known for abuse → moderate risk signal
- Domain name mimics known brand (e.g., `amaz0n-verify.com`) → high risk signal

**Env var**: None (RDAP is free, python-whois uses RDAP/WHOIS)

---

## Parallel Execution Strategy

All threat intel checks run **concurrently** using `asyncio.gather()` with individual
timeouts per source.

```python
async def check_all(entities: ExtractedEntities) -> ThreatIntelResults:
    tasks = []

    for url in entities.urls:
        tasks.append(check_with_timeout(safe_browsing.check(url), timeout=3.0))
        tasks.append(check_with_timeout(phishtank.check(url), timeout=3.0))
        tasks.append(check_with_timeout(urlhaus.check(url), timeout=3.0))

    for domain in entities.domains:
        tasks.append(check_with_timeout(spamhaus.check(domain), timeout=2.0))
        tasks.append(check_with_timeout(whois_lookup.check(domain), timeout=5.0))

    results = await asyncio.gather(*tasks, return_exceptions=True)
    # Exceptions from individual sources are logged and treated as "source unavailable"
    return aggregate_results(results)
```

**Timeouts per source**:
| Source | Timeout | Reason |
|--------|---------|--------|
| Spamhaus (DNS) | 2s | DNS should be fast |
| Safe Browsing | 3s | REST API, usually fast |
| PhishTank | 3s | REST API, occasionally slow |
| URLhaus | 3s | REST API, usually fast |
| WHOIS | 5s | WHOIS servers can be slow |

**Total threat intel budget**: ~5 seconds max (worst case, all sources hit timeout).
Typical case: ~500ms (limited by slowest successful source).

---

## Result Aggregation

Each source produces a `ThreatResult`:
```python
@dataclass
class ThreatResult:
    source: str          # "phishtank", "safe_browsing", etc.
    entity: str          # the URL/domain/IP checked
    is_flagged: bool     # was it flagged by this source?
    threat_type: str     # source-specific threat type
    confidence: float    # 0.0-1.0 (some sources give confidence)
    details: dict        # source-specific details
    response_time_ms: int
```

Aggregation logic:
1. **Any source flags it** → include in evidence with source attribution
2. **Multiple sources flag it** → higher confidence, explicitly noted in explanation
3. **No sources flag it** → note that "No known threats found in databases" (LLM analysis still applies)
4. **Source unavailable** → note which sources were checked and which were unavailable

---

## Caching Strategy

| Data | Cache Duration | Storage |
|------|---------------|---------|
| Safe Browsing results | 5 minutes | Redis |
| PhishTank results | 10 minutes | Redis |
| URLhaus results | 5 minutes | Redis |
| Spamhaus results | 15 minutes | Redis |
| WHOIS data | 24 hours | Redis |
| Source availability status | 1 minute | Redis |

Cache key format: `threat:{source}:{sha256(entity)}`

If a source has been failing consistently (>3 failures in 5 minutes), it's marked as
"degraded" and skipped for 1 minute to avoid wasting time on timeouts.

---

## Monitoring

### Metrics (Prometheus)

| Metric | Type | Labels |
|--------|------|--------|
| `threat_intel_requests_total` | Counter | source, result (hit/miss/error/timeout) |
| `threat_intel_response_seconds` | Histogram | source |
| `threat_intel_flagged_total` | Counter | source, threat_type |
| `threat_intel_source_available` | Gauge | source (1=up, 0=down) |
| `threat_intel_cache_hits_total` | Counter | source |

### Alerts

| Alert | Condition | Severity |
|-------|-----------|----------|
| Source down | > 5 failures in 5 min | Warning |
| All sources down | 0 sources responding | Critical |
| High flag rate | > 50% of scans flagged by any source in 1 hour | Info (possible false positive wave) |
| Slow responses | p95 > 5s for any source | Warning |

---

## India-Specific Threat Intel (Future)

| Source | What | Phase |
|--------|------|-------|
| **TRAI DND Registry** | Check if sender is registered / DND violations | Post-MVP |
| **Cyber Crime Portal** | Cross-reference with Indian cybercrime database | Post-MVP |
| **UPI fraud database** | Known fraudulent UPI IDs (community-sourced) | Post-MVP |
| **Indian bank phishing domains** | Curated list of fake bank domains targeting Indian banks | Post-MVP |
