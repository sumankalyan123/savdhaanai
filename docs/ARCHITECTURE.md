# Savdhaan AI — System Architecture

> Last updated: 2026-02-20

---

## High-Level Architecture

```
                          ┌─────────────────────────────────┐
                          │         Client Layer             │
                          │  (Web / Mobile / Bot / Extension)│
                          └────────────┬────────────────────┘
                                       │ HTTPS
                                       ▼
                          ┌─────────────────────────────────┐
                          │        API Gateway / LB          │
                          │  (Nginx / Cloud Load Balancer)   │
                          └────────────┬────────────────────┘
                                       │
                                       ▼
┌──────────────────────────────────────────────────────────────────────┐
│                        FastAPI Application                           │
│                                                                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌───────────────────┐   │
│  │  Routes   │  │  Schemas │  │Middleware │  │ Dependency Inject │   │
│  │ /scan     │  │ Pydantic │  │ Auth      │  │ DB sessions       │   │
│  │ /card     │  │ v2       │  │ RateLimit │  │ Service instances  │   │
│  │ /report   │  │          │  │ CORS      │  │ Config             │   │
│  │ /health   │  │          │  │ Logging   │  │                    │   │
│  └─────┬─────┘  └──────────┘  └──────────┘  └───────────────────┘   │
│        │                                                              │
│        ▼                                                              │
│  ┌────────────────────────────────────────────────────────────────┐  │
│  │                      Service Layer                             │  │
│  │                                                                │  │
│  │  ┌──────────────┐    ┌─────────────────┐    ┌──────────────┐  │  │
│  │  │ ScanService  │───▶│ EntityExtractor │───▶│ ThreatIntel  │  │  │
│  │  │ (orchestrator)│   │ (Claude tool_use)│   │ (parallel)   │  │  │
│  │  └──────┬───────┘    └─────────────────┘    └──────┬───────┘  │  │
│  │         │                                          │          │  │
│  │         ▼                                          ▼          │  │
│  │  ┌──────────────┐    ┌─────────────────┐    ┌──────────────┐  │  │
│  │  │ OCRService   │    │  Classifier     │    │ ActionEngine │  │  │
│  │  │ (Vision/Tess)│    │ (Claude tool_use)│   │              │  │  │
│  │  └──────────────┘    └─────────────────┘    └──────────────┘  │  │
│  │                                                                │  │
│  │  ┌──────────────┐    ┌─────────────────┐                      │  │
│  │  │ ScamCard     │    │ ReportService   │                      │  │
│  │  │ (generator)  │    │ (feedback)      │                      │  │
│  │  └──────────────┘    └─────────────────┘                      │  │
│  └────────────────────────────────────────────────────────────────┘  │
└──────────────────────┬──────────────────────┬────────────────────────┘
                       │                      │
           ┌───────────▼──────────┐  ┌────────▼─────────┐
           │    PostgreSQL 16     │  │      Redis        │
           │                      │  │                    │
           │  - Scans             │  │  - Rate limiting   │
           │  - Scam cards        │  │  - Response cache  │
           │  - User reports      │  │  - Session store   │
           │  - Users             │  │  - Celery broker   │
           │  - Audit log         │  │                    │
           └──────────────────────┘  └────────┬──────────┘
                                              │
                                     ┌────────▼──────────┐
                                     │  Celery Workers    │
                                     │                    │
                                     │  - Async threat    │
                                     │    intel lookups   │
                                     │  - Analytics       │
                                     │    aggregation     │
                                     │  - Scam card       │
                                     │    image rendering │
                                     └────────────────────┘
```

---

## Technology Stack — Detailed Rationale

### Core Runtime

| Component | Choice | Version | Why |
|-----------|--------|---------|-----|
| **Language** | Python | 3.12+ | Best AI/ML ecosystem, Anthropic SDK, async support, massive community |
| **Web framework** | FastAPI | 0.115+ | Async-native, Pydantic v2 built-in, auto OpenAPI, top performance for Python |
| **ASGI server** | Uvicorn | 0.34+ | Industry standard, HTTP/2 support, production-proven |
| **Process manager** | Gunicorn + Uvicorn workers | — | Multi-process for production, Uvicorn for async within each process |

**Why FastAPI over alternatives:**
- **vs Django REST**: FastAPI is 3-5x faster, async-native, Pydantic schemas are cleaner than serializers. Django's ORM is sync-first.
- **vs Flask**: No async support, no built-in validation, requires many extensions.
- **vs Express/Node**: Python has better AI/ML libraries, Anthropic SDK is more mature in Python.
- **vs Go/Rust**: Speed isn't the bottleneck (LLM calls are). Python's ecosystem and developer velocity win.

### Data Layer

| Component | Choice | Version | Why |
|-----------|--------|---------|-----|
| **Primary DB** | PostgreSQL | 16 | UUID gen, JSONB, full-text search, partitioning, battle-tested |
| **ORM** | SQLAlchemy | 2.0+ | Async support, type-safe queries, mature migration tool (Alembic) |
| **Migrations** | Alembic | 1.14+ | Standard for SQLAlchemy, auto-generates migration scripts |
| **Cache / Broker** | Redis | 7.4+ | Sub-ms latency, Lua scripting for rate limiting, Celery broker |
| **Object storage** | S3 / MinIO | — | Scam card images, uploaded screenshots. MinIO for local dev. |

**Why PostgreSQL over alternatives:**
- **vs MySQL**: Better JSONB support (scan results are semi-structured), UUID native, better partitioning.
- **vs MongoDB**: Scam detection needs relational integrity (scans → entities → threat results). Schema enforcement prevents data corruption in a safety-critical product.
- **vs SQLite**: No concurrent write support, not suitable for production.

### AI / ML Layer

| Component | Choice | Why |
|-----------|--------|-----|
| **LLM provider** | Anthropic Claude | Best structured output via tool_use, strong reasoning, safety-focused |
| **Fast model** | claude-sonnet-4-6 | 95% of scans — fast, cost-effective, reliable for clear-cut scams |
| **Complex model** | claude-opus-4-6 | 5% of scans — ambiguous cases, multi-language, sophisticated social engineering |
| **LLM interaction** | Structured tool_use | Not free-text. Every extraction/classification is a tool call with typed schema |
| **OCR (primary)** | Google Cloud Vision | Multi-language, handles messy screenshots, handwriting, low-res images |
| **OCR (fallback)** | Tesseract via pytesseract | Free, offline, good for dev. Auto-fallback if Vision API is unavailable |
| **Embeddings** | Voyage AI / Anthropic | Future: scam similarity clustering. Not needed for MVP 1 |

**Two-tier LLM strategy:**
```
Incoming scan
     │
     ▼
┌─────────────┐    confidence >= 0.85    ┌──────────────┐
│ Claude Sonnet│───────────────────────▶ │ Return result │
│ (fast, cheap)│                         └──────────────┘
└──────┬──────┘
       │ confidence < 0.85
       ▼
┌─────────────┐
│ Claude Opus  │───────────────────────▶ Return result
│ (deep reason)│
└─────────────┘
```

### Threat Intelligence

| Source | Protocol | What It Checks | Latency |
|--------|----------|---------------|---------|
| **Google Safe Browsing** | REST API v4 | URL reputation (malware, social engineering, unwanted software) | ~100ms |
| **PhishTank** | REST API | Known phishing URLs (community-verified database) | ~200ms |
| **URLhaus** | REST API | Malware distribution URLs | ~150ms |
| **Spamhaus** | DNS queries (DQS) | Domain/IP blocklists (SBL, XBL, DBL) | ~50ms |
| **WHOIS** | RDAP / python-whois | Domain age, registrar, registration date | ~500ms |

All sources queried **in parallel** via `asyncio.gather()`. Total threat intel latency ≈ max single source (~500ms) rather than sum (~1000ms).

### Anti-Abuse Detection

| Component | Choice | Why |
|-----------|--------|-----|
| **Abuse scoring** | Custom service (Redis-backed) | Real-time behavioral scoring per API key |
| **Semantic fingerprinting** | SimHash / MinHash | Group scam variants by structural similarity |
| **IP reputation** | Internal + external signals | Detect VPN/proxy/datacenter automated testing |
| **Progressive degradation** | Middleware layer | Reduce evidence detail as abuse score rises |

**How it works in the scan pipeline:**
```
Request arrives
     │
     ▼
┌─────────────────────┐
│  Abuse Score Check   │ ← Redis: scan frequency, content similarity,
│  (middleware)        │   flag rate, entity reuse, burst detection
└──────────┬──────────┘
           │
           ▼
     Score 0-30 → Full evidence response
     Score 31-60 → Simplified evidence (no source names)
     Score 61-80 → Verdict only + CAPTCHA challenge
     Score 81-100 → Hard throttle (1 scan/hour) + account flagged
```

Scammer testing also generates **free threat intel** — new URLs, phone numbers,
UPI IDs, and scam templates harvested from their test content are fed back into
detection for all users. See [LIMITATIONS.md](LIMITATIONS.md) for full strategy.

### Task Queue

| Component | Choice | Why |
|-----------|--------|-----|
| **Task queue** | Celery | Mature, battle-tested, good monitoring (Flower), retry policies |
| **Broker** | Redis | Already in stack, low latency, reliable for task queue workloads |
| **Result backend** | Redis | Fast result storage, auto-expiry for completed tasks |

**What runs in Celery (vs inline async):**
- Threat intel lookups that may be slow (WHOIS can take 500ms+) — run async for non-blocking
- Analytics aggregation (daily/weekly scam trends)
- Scam card image rendering (CPU-bound, offload from API workers)
- Cleanup tasks (delete expired raw content, purge old sessions)
- Abuse score recalculation and account flagging

### Infrastructure

| Component | Choice | Why |
|-----------|--------|-----|
| **Containerization** | Docker | Standard, reproducible environments |
| **Local dev** | Docker Compose | One command to start all services |
| **Production** | Kubernetes (EKS/GKE) | Auto-scaling, rolling deploys, health checks, service mesh |
| **CI/CD** | GitHub Actions | Native GitHub integration, good free tier, matrix builds |
| **Monitoring** | Prometheus + Grafana | Industry standard, excellent dashboards, alerting |
| **Logging** | Structured JSON → ELK or CloudWatch | Queryable logs, correlation IDs across services |
| **Error tracking** | Sentry | Real-time error alerts, stack traces, performance monitoring |
| **CDN** | CloudFront or Cloudflare | Scam card pages and images need global low-latency delivery |

### Frontend (MVP 2+)

| Component | Choice | Version | Why |
|-----------|--------|---------|-----|
| **Web framework** | Next.js | 15 (App Router) | SSR for scam card SEO, React ecosystem, Vercel deployment |
| **Styling** | Tailwind CSS | 4.x | Utility-first, fast iteration, consistent design tokens |
| **Auth** | NextAuth.js (Auth.js) | 5.x | Email + OAuth providers, session management, JWT/database sessions |
| **State** | Zustand or React Query | — | Lightweight, no boilerplate. React Query for server state. |
| **Mobile** | React Native (Expo) | SDK 52+ | Cross-platform, shared TS/JS, Expo simplifies builds and OTA updates |
| **E2E testing** | Playwright | 1.50+ | Cross-browser, reliable, good Next.js integration |

**Why Next.js over alternatives:**
- **vs plain React (Vite)**: Scam card pages MUST be server-rendered for Open Graph meta tags. WhatsApp/iMessage/Twitter previews require SSR.
- **vs Remix**: Next.js has larger ecosystem, better Vercel integration, more mature App Router.
- **vs SvelteKit**: Smaller ecosystem, harder to hire for, less component library support.
- **vs Nuxt (Vue)**: React has larger talent pool, better React Native code sharing story.

---

## Request Flow — Full Scan Pipeline

```
1. Client sends POST /api/v1/scan
   Body: { "content": "...", "content_type": "text|image", "channel": "sms|email|whatsapp|..." }
   Headers: X-API-Key: <key>

2. Middleware:
   ├── Authenticate API key → load user/tier
   ├── Rate limit check (Redis token bucket)
   ├── Request validation (Pydantic schema)
   └── Assign correlation ID (X-Request-Id)

3. ScanService.execute(scan_request):
   │
   ├── IF image:
   │   └── OCRService.extract_text(image)
   │       ├── Try Google Vision API
   │       └── Fallback to Tesseract if Vision fails
   │
   ├── EntityExtractor.extract(text):
   │   └── Claude API tool_use call → structured extraction
   │       Returns: { urls: [...], phones: [...], emails: [...], crypto: [...], upi: [...] }
   │
   ├── ThreatIntel.check_all(entities):  [PARALLEL]
   │   ├── PhishTank.check(urls)
   │   ├── GoogleSafeBrowsing.check(urls)
   │   ├── URLhaus.check(urls)
   │   ├── Spamhaus.check(domains, ips)
   │   └── WHOIS.check(domains) → domain age
   │
   ├── Classifier.classify(text, entities, threat_results):
   │   └── Claude API tool_use call → structured classification
   │       Returns: { scam_type, risk_score, risk_level, explanation, evidence: [...] }
   │
   ├── ActionEngine.recommend(classification):
   │   └── Rule-based + scam-type-specific action list
   │       Returns: [ { action, priority, description } ]
   │
   ├── ScamCard.generate(scan_result):
   │   └── Create card record + render shareable image (async via Celery)
   │       Returns: { card_id, card_url, image_url }
   │
   └── Persist scan result to PostgreSQL
       (raw content scheduled for deletion after retention window)

4. Return response:
   {
     "ok": true,
     "data": {
       "scan_id": "uuid",
       "risk_score": 87,
       "risk_level": "critical",
       "scam_type": "phishing",
       "explanation": "This message contains a link to a known phishing domain...",
       "evidence": [
         { "type": "url_flagged", "source": "PhishTank", "detail": "..." },
         { "type": "domain_age", "source": "WHOIS", "detail": "Domain registered 2 days ago" }
       ],
       "actions": [
         { "action": "do_not_click", "priority": "critical", "description": "..." },
         { "action": "block_sender", "priority": "high", "description": "..." },
         { "action": "report_phishing", "priority": "medium", "description": "..." }
       ],
       "scam_card": {
         "card_id": "uuid",
         "card_url": "https://savdhaan.ai/card/abc123",
         "image_url": "https://cdn.savdhaan.ai/cards/abc123.png"
       },
       "entities": { ... },
       "processing_time_ms": 2340
     }
   }
```

---

## Security Architecture

### Data Flow Security
- **TLS everywhere**: All API traffic over HTTPS. Internal services use mTLS in production.
- **Input validation**: Pydantic schemas reject malformed input before it reaches business logic.
- **Output sanitization**: LLM outputs are validated against expected schemas. No raw LLM text in responses.

### Authentication & Authorization
- **MVP 1**: API key-based auth. Keys stored as bcrypt hashes in PostgreSQL.
- **MVP 2+**: JWT tokens for web/mobile users, API keys for programmatic access.
- **Rate limiting**: Redis-backed token bucket per API key / user, tiered by plan.

### Privacy
- **Minimal retention**: Raw message content deleted after processing (configurable, default 1 hour).
- **No PII logging**: Structured logs exclude message content, phone numbers, emails.
- **Scan results**: Store classification + metadata, not the original content.
- **User control**: Users can delete their scan history at any time.

### Threat Model
- **Prompt injection**: LLM inputs are structured tool_use calls, not free-text. Output is validated against tool schemas.
- **Malicious uploads**: Image uploads validated (type, size, dimensions) before OCR processing.
- **Rate abuse**: Multi-layer rate limiting (API key + IP + global).
- **Data exfiltration**: No endpoint exposes bulk data. Pagination enforced.
- **Adversarial testing**: Scammers using the platform to refine scams. Mitigated by behavioral abuse scoring, progressive evidence redaction, and intelligence harvesting. See [LIMITATIONS.md](LIMITATIONS.md).

### Honest Messaging
- Scan results always include what was checked and what couldn't be checked.
- No absolute language ("safe", "definitely a scam"). Always qualified confidence.
- Low-risk results explicitly state "no automated system is perfect."
- See [LIMITATIONS.md](LIMITATIONS.md) for full messaging framework.

---

## Scalability Strategy

### MVP 1 (Single-Region)
```
1x FastAPI (2-4 Gunicorn workers)
1x PostgreSQL 16
1x Redis 7
1-2x Celery workers
```
Handles: ~50-100 concurrent users, ~10K scans/day

### Growth (Multi-Instance)
```
2-4x FastAPI instances behind load balancer
1x PostgreSQL with read replicas
1x Redis Cluster (3 nodes)
2-4x Celery workers
CDN for scam card images
```
Handles: ~500-1000 concurrent users, ~100K scans/day

### Scale (Kubernetes)
```
Auto-scaling FastAPI pods (HPA based on CPU/request rate)
PostgreSQL managed (RDS/Cloud SQL) with read replicas
Redis managed (ElastiCache/Memorystore) cluster mode
Auto-scaling Celery worker pods
S3 + CloudFront for all static assets
Multi-region deployment for latency
```
Handles: ~10K+ concurrent users, ~1M+ scans/day
