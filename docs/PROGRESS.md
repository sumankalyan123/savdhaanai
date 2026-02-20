# Savdhaan AI — Build Progress

> Tracks what's been built, what's working, and what's next.

---

## Current Status: Phase 0 + Sprint 1-3 scaffolding COMPLETE

**Date**: 2026-02-20
**Commit**: `4c0da6f` — "Add MVP 1 backend: full scan pipeline, API, models, tests"
**Repo**: https://github.com/sumankalyan123/savdhaanai

---

## What's Done

### Phase 0 — Foundation [COMPLETE]

| Task | Status | File(s) |
|------|--------|---------|
| Python project setup | Done | `pyproject.toml` |
| Docker setup | Done | `infra/docker/Dockerfile`, `infra/docker/docker-compose.yml` |
| Project scaffolding | Done | All `__init__.py`, package structure |
| Database models | Done | `src/models/` (6 model files, 11 tables) |
| Alembic setup | Done | `alembic.ini`, `alembic/env.py` |
| Dev tooling | Done | `Makefile`, ruff config, pytest config |
| Core config | Done | `src/core/config.py` (pydantic-settings) |
| Exception handling | Done | `src/core/exceptions.py` + `src/api/middleware/error_handler.py` |
| Structured logging | Done | `src/api/middleware/logging.py` + request ID middleware |
| Git + GitHub | Done | Repo initialized, pushed to GitHub |
| Environment template | Done | `.env.example` with all vars documented |

### Sprint 1 — Entity Extraction + Threat Intel [COMPLETE]

| Task | Status | File(s) |
|------|--------|---------|
| Entity extractor (regex + LLM) | Done | `src/services/entity_extractor.py` |
| URL parser (normalize, shorten detection) | Done | `src/utils/url_parser.py` |
| Phone parser (international + India) | Done | `src/utils/phone_parser.py` |
| Email, UPI, crypto extraction | Done | `src/utils/phone_parser.py` |
| Google Safe Browsing integration | Done | `src/services/threat_intel.py` |
| PhishTank integration | Done | `src/services/threat_intel.py` |
| URLhaus integration | Done | `src/services/threat_intel.py` |
| WHOIS domain age check | Done | `src/services/threat_intel.py` |
| Parallel threat intel execution | Done | `asyncio.gather()` in `threat_intel.py` |
| Unit tests (URL, phone, text) | Done | `tests/unit/` (30 tests passing) |

### Sprint 2 — Classification + Scan Pipeline [COMPLETE]

| Task | Status | File(s) |
|------|--------|---------|
| LLM classifier (Claude tool_use) | Done | `src/services/classifier.py` |
| Fallback classifier (no LLM) | Done | `src/services/classifier.py` |
| Action engine (per scam type) | Done | `src/services/action_engine.py` |
| OCR service (Tesseract + Vision) | Done | `src/services/ocr_service.py` |
| Image utilities | Done | `src/utils/image_utils.py` |
| Scan orchestrator (full pipeline) | Done | `src/services/scan_service.py` |
| PII redaction utilities | Done | `src/utils/text_sanitizer.py` |

### Sprint 3 — API + Cards + Polish [COMPLETE]

| Task | Status | File(s) |
|------|--------|---------|
| POST /scan endpoint (text) | Done | `src/api/routes/scan.py` |
| POST /scan/image endpoint | Done | `src/api/routes/scan.py` |
| GET /scan/{id} endpoint | Done | `src/api/routes/scan.py` |
| GET /card/{short_id} endpoint | Done | `src/api/routes/card.py` |
| POST /report endpoint | Done | `src/api/routes/report.py` |
| GET /health endpoint | Done | `src/api/routes/health.py` |
| Scam card generator | Done | `src/services/scam_card.py` |
| API key auth middleware | Done | `src/api/deps.py` |
| Pydantic request/response schemas | Done | `src/api/schemas/` (4 files) |
| Error handler middleware | Done | `src/api/middleware/error_handler.py` |
| Anti-abuse detector | Done | `src/services/abuse_detector.py` |
| Honest messaging framework | Done | Built into `scan_service.py` |
| Celery workers (placeholder) | Done | `src/workers/` |
| Report service | Done | `src/services/report_service.py` |
| Seed script (scam taxonomy) | Done | `scripts/seed_scam_taxonomy.py` |

### Documentation [COMPLETE]

| Doc | Status |
|-----|--------|
| `CLAUDE.md` | Done — project guide |
| `README.md` | Done — overview |
| `docs/PRODUCT_VISION.md` | Done — full vision, strategy, revenue model |
| `docs/MVP_SCOPE.md` | Done — MVP 1/2/3 scope, success criteria |
| `docs/ARCHITECTURE.md` | Done — system design, tech rationale |
| `docs/API_DESIGN.md` | Done — all endpoints, schemas, error codes |
| `docs/DATABASE_SCHEMA.md` | Done — 11 tables, ERD, indexes |
| `docs/THREAT_INTEL.md` | Done — 5 sources, integration details |
| `docs/SECURITY.md` | Done — auth, encryption, RBAC, compliance |
| `docs/DEPLOYMENT.md` | Done — AWS, Docker, K8s, CI/CD, monitoring |
| `docs/ROADMAP.md` | Done — sprint plan, milestones |
| `docs/LIMITATIONS.md` | Done — anti-abuse, honest messaging |

---

## By the Numbers

| Metric | Count |
|--------|-------|
| Python source files | 35 |
| Lines of code (src/) | ~2,500 |
| Lines of code (tests/) | ~250 |
| Lines of docs | ~4,000 |
| Database tables | 11 |
| API endpoints | 6 |
| Threat intel sources | 4 (+ Spamhaus ready) |
| Scam types in taxonomy | 18 |
| Tests passing | 30 |
| Lint errors | 0 |

---

## What's NOT Done Yet (MVP 1 remaining)

These items from the roadmap are scaffolded but need real-world testing and refinement:

| Task | Status | Notes |
|------|--------|-------|
| Run Alembic first migration | Pending | Need PostgreSQL running (`make dev`) |
| Seed scam taxonomy to DB | Pending | Run `make seed` after migration |
| Redis caching for threat intel | Pending | Cache layer not implemented yet |
| Rate limiting middleware | Pending | Schema ready, middleware not wired |
| Spamhaus DNS integration | Pending | Service exists, DNS query not implemented |
| Card image renderer (PNG) | Pending | Celery task placeholder exists |
| Anti-abuse scoring (Redis) | Pending | DB model ready, real-time scoring not wired |
| Semantic fingerprinting | Pending | DB model ready, SimHash not implemented |
| Intelligence harvesting | Pending | Pipeline placeholder, not wired |
| Performance testing (p95 < 3s) | Pending | Need real API keys to test |
| Integration tests with DB | Pending | Only health endpoint tested with DB |
| CI/CD pipeline (GitHub Actions) | Pending | No workflow file yet |
| Pre-commit hooks | Pending | Config not created yet |
| OpenAPI spec review | Pending | Auto-generated, needs review |

---

## What's Next

### Immediate (to make it runnable end-to-end)

1. **`make dev`** — start Docker Compose, verify all services connect
2. **Run first Alembic migration** — create all 11 tables in PostgreSQL
3. **Seed scam taxonomy** — populate reference data
4. **Add `.env` with real API keys** — Anthropic key minimum for scan to work
5. **Test a real scan** — `curl POST /api/v1/scan` with a phishing message

### Then (Sprint 3 polish)

6. Redis caching for threat intel results
7. Rate limiting middleware (token-bucket)
8. GitHub Actions CI pipeline
9. Integration tests with mocked external APIs
10. Performance benchmarking

### After MVP 1 (Phase 2)

- Next.js 15 web app
- User auth (NextAuth.js)
- Scan history dashboard
- Public scam card pages with OG tags

---

## Git History

| Date | Commit | Description |
|------|--------|-------------|
| 2026-02-20 | `7fc5256` | Initial commit: project documentation and architecture |
| 2026-02-20 | `4c0da6f` | Add MVP 1 backend: full scan pipeline, API, models, tests |
