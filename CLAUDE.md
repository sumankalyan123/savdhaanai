# Savdhaan AI - Project Guide

## Project Overview

**Savdhaan AI** is an AI risk copilot that helps people make safer decisions — starting with scam detection, expanding to job offers, leases, investments, and contracts.

Phase 1 (MVP 1): Scam detection — the viral hook. Paste suspicious message → get evidence-based risk assessment + shareable scam card.
Phase 2+: Broader risk categories — job offers, rental leases, investment pitches, contract terms. Same pipeline, different analysis frameworks.

- **Domain**: savdhaan.ai
- **Primary markets**: India (growth), USA (revenue), UK/Canada/Australia (expansion)
- **Primary channels**: Text/email/messaging (NOT voice calls)
- **Strategy**: Scam detection for free viral acquisition → Decision risk copilot for premium monetization

## Documentation

Detailed docs live in `docs/` — always check these before making architectural decisions:

- **[docs/PRODUCT_VISION.md](docs/PRODUCT_VISION.md)** — Full product vision: hook → habit → platform strategy, all risk categories, revenue model
- **[docs/MVP_SCOPE.md](docs/MVP_SCOPE.md)** — MVP 1, 2, 3 scope, success criteria, scam taxonomy
- **[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)** — System architecture, tech rationale, request flow, security model
- **[docs/API_DESIGN.md](docs/API_DESIGN.md)** — All endpoints, request/response schemas, error codes
- **[docs/DATABASE_SCHEMA.md](docs/DATABASE_SCHEMA.md)** — Table definitions, ERD, indexes, data retention
- **[docs/THREAT_INTEL.md](docs/THREAT_INTEL.md)** — All threat intel sources, integration details, caching
- **[docs/SECURITY.md](docs/SECURITY.md)** — Auth (API key + JWT + OAuth), encryption, RBAC, audit logging, GDPR/DPDP compliance, secrets management, incident response
- **[docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)** — AWS hosting, Docker, Kubernetes, CI/CD pipeline, monitoring, backup/DR, cost estimates
- **[docs/ROADMAP.md](docs/ROADMAP.md)** — Phased delivery plan, sprint breakdown, milestones
- **[docs/LIMITATIONS.md](docs/LIMITATIONS.md)** — Honest limitations, adversarial resilience, anti-abuse strategy, user messaging framework
- **[docs/PROGRESS.md](docs/PROGRESS.md)** — Build progress tracker, what's done, what's next

## Tech Stack

### Backend
- **Language**: Python 3.12+
- **Framework**: FastAPI (async, high performance)
- **Task queue**: Celery + Redis
- **Database**: PostgreSQL 16 (primary), Redis (cache + rate limiting + sessions)
- **ORM**: SQLAlchemy 2.0 (async) + Alembic (migrations)
- **Object storage**: S3-compatible (AWS S3 or MinIO for local dev)

### AI / ML
- **LLM**: Anthropic Claude API (claude-sonnet-4-6 for speed, claude-opus-4-6 for complex cases)
  - Use structured tool_use / function calling for entity extraction
  - Use tool_use for scam classification with grounded reasoning
- **OCR**: Google Cloud Vision API (primary), Tesseract (fallback/local dev)
- **Embeddings**: For scam similarity clustering (future)

### Threat Intelligence
- **Spamhaus** - Domain/IP blocklist queries
- **PhishTank** - Known phishing URL database
- **URLhaus** - Malware distribution URL database
- **Google Safe Browsing** - URL reputation API
- **WHOIS** - Domain age and registration checks

### Frontend (Phase 2 - after API is solid)
- **Web**: Next.js 15 (App Router)
- **Mobile**: React Native (Expo)
- **Styling**: Tailwind CSS

### Infrastructure
- **Containerization**: Docker + Docker Compose (dev), Kubernetes (prod)
- **CI/CD**: GitHub Actions
- **Monitoring**: Prometheus + Grafana
- **Logging**: Structured JSON logs → ELK or CloudWatch
- **APM**: Sentry

## Project Structure

```
savdhaan-ai/
├── CLAUDE.md                    # This file
├── README.md                    # Project overview
├── docs/                        # All documentation
│   ├── MVP_SCOPE.md
│   ├── ARCHITECTURE.md
│   ├── API_DESIGN.md
│   ├── DATABASE_SCHEMA.md
│   ├── THREAT_INTEL.md
│   ├── SECURITY.md
│   ├── DEPLOYMENT.md
│   ├── LIMITATIONS.md
│   ├── PRODUCT_VISION.md
│   └── ROADMAP.md
├── src/
│   ├── api/                     # FastAPI routes and request/response schemas
│   │   ├── __init__.py
│   │   ├── routes/              # Route handlers grouped by domain
│   │   ├── schemas/             # Pydantic request/response models
│   │   ├── middleware/          # Auth, rate limiting, CORS, logging
│   │   └── deps.py             # Dependency injection
│   ├── core/                    # App configuration and shared kernel
│   │   ├── __init__.py
│   │   ├── config.py            # Settings via pydantic-settings (env vars)
│   │   ├── security.py          # Auth, JWT, API keys
│   │   ├── exceptions.py        # Custom exception hierarchy
│   │   └── constants.py         # Enums, scam taxonomy, risk levels
│   ├── services/                # Business logic layer
│   │   ├── __init__.py
│   │   ├── scan_service.py      # Orchestrates the full scan pipeline
│   │   ├── ocr_service.py       # Image → text extraction
│   │   ├── entity_extractor.py  # LLM-based entity extraction (URLs, phones, etc.)
│   │   ├── threat_intel.py      # Aggregates reputation checks
│   │   ├── classifier.py        # LLM-based scam classification + explanation
│   │   ├── action_engine.py     # Generates recommended actions per scam type
│   │   ├── scam_card.py         # Generates shareable scam card (image + link)
│   │   ├── report_service.py    # Handles user reports and feedback
│   │   └── abuse_detector.py    # Anti-abuse scoring, behavioral detection, response degradation
│   ├── models/                  # SQLAlchemy ORM models
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── scan.py
│   │   ├── scam_card.py
│   │   ├── report.py
│   │   └── abuse.py             # Abuse events, scores, semantic fingerprints
│   ├── workers/                 # Celery async tasks
│   │   ├── __init__.py
│   │   ├── threat_check.py      # Background threat intel lookups
│   │   └── analytics.py         # Aggregation and digest generation
│   └── utils/                   # Pure utility functions
│       ├── __init__.py
│       ├── url_parser.py        # URL normalization and extraction
│       ├── phone_parser.py      # Phone number parsing and normalization
│       ├── text_sanitizer.py    # PII redaction helpers
│       └── image_utils.py       # Image preprocessing for OCR
├── tests/
│   ├── conftest.py              # Fixtures, test DB, test client
│   ├── unit/                    # Unit tests (no external calls)
│   ├── integration/             # Tests with DB and external services (mocked)
│   └── fixtures/                # Sample scam messages, screenshots, etc.
├── scripts/
│   ├── seed_scam_taxonomy.py    # Populate scam type reference data
│   └── load_threat_feeds.py     # Initial load of threat intel data
├── infra/
│   ├── docker/
│   │   ├── Dockerfile
│   │   └── docker-compose.yml
│   ├── k8s/                     # Kubernetes manifests (prod)
│   └── terraform/               # Infrastructure as code (future)
├── alembic/                     # Database migrations
│   └── versions/
├── alembic.ini
├── pyproject.toml               # Project deps and tooling config
├── .env.example                 # Template for environment variables
├── .gitignore
└── Makefile                     # Common dev commands
```

## Coding Conventions

### Python
- **Formatter**: `ruff format` (line length 100)
- **Linter**: `ruff check` with strict rules
- **Type hints**: Required on all function signatures. Use `from __future__ import annotations`.
- **Async**: All I/O-bound operations must be async. Use `httpx.AsyncClient` for HTTP calls.
- **Naming**: snake_case for functions/variables, PascalCase for classes, UPPER_SNAKE for constants.
- **Imports**: Group as stdlib → third-party → local. Ruff handles sorting.

### API Design
- RESTful with consistent response envelope: `{"ok": bool, "data": ..., "error": ...}`
- Use Pydantic v2 models for all request/response schemas
- Version prefix: `/api/v1/`
- Rate limiting on all public endpoints
- All timestamps in UTC ISO 8601

### Database
- All tables have `id` (UUID), `created_at`, `updated_at` columns
- Use Alembic for all schema changes — never modify DB directly
- Soft delete where needed (`deleted_at` timestamp)
- Index all foreign keys and frequently queried columns

### Testing
- `pytest` with `pytest-asyncio` for async tests
- Minimum 80% coverage on services/
- All external API calls mocked in tests
- Use fixtures/ for sample scam data

### Git
- Branch naming: `feat/`, `fix/`, `docs/`, `refactor/`, `test/`
- Commit messages: imperative mood, concise ("Add scan endpoint", not "Added scan endpoint")
- PR required for main — no direct pushes
- Squash merge to main

### Security
- Never log PII (message content, phone numbers, email addresses)
- Never store raw message content longer than the processing window (configurable, default 1 hour)
- All secrets via environment variables — never hardcoded
- Input validation on all user-facing endpoints
- Rate limiting: 10 scans/hour free tier, 100/hour premium

### Error Handling
- Custom exception hierarchy rooted in `SavdhaanError`
- All exceptions caught at middleware level and returned as structured JSON
- External API failures degrade gracefully — partial results are better than no results
- Never expose internal stack traces to users

## Key Design Principles

1. **Evidence-grounded**: Every scam classification must cite specific signals (URL flagged, domain age, pattern match). Never rely on LLM "vibes" alone.
2. **Privacy by default**: Process and discard. Minimal retention. User controls what's saved.
3. **Graceful degradation**: If PhishTank is down, still return LLM analysis + other intel. Never fail completely.
4. **Share-first**: The shareable scam card is a core feature, not an afterthought. Optimize for WhatsApp/iMessage forwarding.
5. **Speed**: Target <3 seconds for a full scan result. Use parallel threat intel checks.

## Common Commands

```bash
make dev          # Start local dev environment (docker-compose up)
make test         # Run all tests
make lint         # Run ruff check + ruff format --check
make migrate      # Run pending Alembic migrations
make seed         # Seed scam taxonomy and test data
make scan-test    # Quick manual scan test via CLI
```

## Environment Variables

See `.env.example` for the full list. Key ones:
- `ANTHROPIC_API_KEY` — Claude API key
- `DATABASE_URL` — PostgreSQL connection string
- `REDIS_URL` — Redis connection string
- `GOOGLE_VISION_API_KEY` — OCR API key
- `PHISHTANK_API_KEY` — PhishTank API key
- `SPAMHAUS_DQS_KEY` — Spamhaus query service key
- `GOOGLE_SAFE_BROWSING_KEY` — Safe Browsing API key
