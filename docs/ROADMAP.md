# Savdhaan AI — Product Roadmap

> Last updated: 2026-02-20

---

## Roadmap Overview

```
  2026
  ────────────────────────────────────────────────────────────────────────
  Feb        Mar        Apr        May        Jun        Jul        Aug
  ├──────────┼──────────┼──────────┼──────────┼──────────┼──────────┤
  │◄── MVP 1: Backend ──►│◄── MVP 2: Web App ──►│◄── MVP 3: Mobile ──►│
  │   Core Pipeline +    │  Next.js + Auth +    │  React Native +     │
  │   API + Threat Intel │  Dashboard + Cards   │  Payments + Bots    │
  └──────────────────────┴──────────────────────┴─────────────────────┘
```

---

## Phase 0 — Foundation (Week 1)

**Goal**: Project setup, local dev environment, core infrastructure.

| Task | Deliverable |
|------|-------------|
| Initialize Python project | `pyproject.toml` with all dependencies |
| Docker setup | `Dockerfile` + `docker-compose.yml` (FastAPI + PostgreSQL + Redis) |
| Project scaffolding | All `__init__.py` files, config module, `.env.example` |
| Database setup | Alembic init, base models, initial migration |
| Dev tooling | Makefile, ruff config, pre-commit hooks, pytest config |
| CI pipeline | GitHub Actions: lint + test + type check on every PR |
| Core config | `pydantic-settings` based config with env var loading |
| Exception handling | Custom exception hierarchy + global error handler middleware |
| Logging | Structured JSON logging with correlation IDs |
| Git setup | Repository, `.gitignore`, branch protection |

**Exit criteria**: `make dev` starts all services, `make test` runs (empty) test suite,
`make lint` passes.

---

## Phase 1 — MVP 1: Core Scan Pipeline (Weeks 2-7)

### Sprint 1 (Weeks 2-3): Entity Extraction + Threat Intel

| Task | Details |
|------|---------|
| Entity extractor service | Claude API tool_use for structured extraction (URLs, phones, emails, crypto, UPI) |
| URL parser utility | Normalize URLs, expand short URLs, extract domains |
| Phone parser utility | Parse and normalize phone numbers (international + Indian formats) |
| Threat intel — Safe Browsing | Google Safe Browsing API v4 integration |
| Threat intel — PhishTank | PhishTank URL lookup integration |
| Threat intel — URLhaus | abuse.ch URL lookup integration |
| Threat intel — Spamhaus | DNS-based domain/IP blocklist queries |
| Threat intel — WHOIS | Domain age and registration lookup |
| Threat intel aggregator | Parallel execution, timeout handling, result aggregation |
| Redis caching layer | Cache threat intel results with TTL |
| Unit tests | Tests for each service with mocked external calls |

### Sprint 2 (Weeks 4-5): Classification + Scan Pipeline

| Task | Details |
|------|---------|
| LLM classifier service | Claude API tool_use for structured scam classification |
| Two-tier model routing | Sonnet for fast path, Opus for ambiguous cases |
| Action engine | Rule-based action recommendations per scam type + risk level |
| OCR service | Google Vision API integration + Tesseract fallback |
| Image utilities | Preprocessing, format validation, size limits |
| Scan orchestrator | Full pipeline: OCR → extract → threat intel → classify → actions |
| Scam taxonomy seed data | Script to populate scam_types reference table |
| Integration tests | End-to-end scan tests with mocked external APIs |

### Sprint 3 (Weeks 6-7): API + Scam Cards + Polish

| Task | Details |
|------|---------|
| POST /scan endpoint | Text + image scan with full pipeline |
| GET /scan/{id} endpoint | Retrieve previous scan result |
| Scam card generator | Create card record + summary from scan result |
| GET /card/{id} endpoint | Public card data (JSON) |
| Card image renderer | Generate shareable PNG image (Celery task) |
| Server-rendered card page | HTML page with Open Graph + Twitter Card meta |
| API key auth | Key generation, hashing, validation middleware |
| Rate limiting | Redis token-bucket, tiered by plan |
| POST /report endpoint | User feedback submission |
| GET /health endpoint | Service health check |
| GET /rate-limit endpoint | Rate limit status |
| Anti-abuse scoring service | Behavioral detection: frequency, similarity, flag rate, entity reuse |
| Progressive response degradation | Reduce evidence detail as abuse score rises (middleware) |
| Semantic fingerprinting | SimHash/MinHash of message structure for cross-account pattern detection |
| Honest messaging framework | All responses include checks_performed, checks_not_available, confidence_note |
| Intelligence harvesting | Extract new URLs/phones/UPI IDs from flagged scans into threat database |
| Performance testing | Ensure <3s p95 for text scans, <5s for image scans |
| Security review | Input validation, PII handling, content retention, adversarial resilience |
| Documentation | OpenAPI spec review, README, deployment guide, LIMITATIONS.md |

**MVP 1 exit criteria**: See [MVP_SCOPE.md](MVP_SCOPE.md) success criteria.

---

## Phase 2 — MVP 2: Web Application (Weeks 8-13)

### Sprint 4 (Weeks 8-9): Next.js Setup + Auth

| Task | Details |
|------|---------|
| Next.js 15 project setup | App Router, Tailwind CSS, TypeScript |
| Auth system | NextAuth.js with email/password + Google OAuth |
| User registration flow | Signup, email verification, login |
| API client | Typed fetch wrapper for backend API |
| Design system | Core components: buttons, cards, inputs, badges, modals |
| Layout | Header, footer, navigation, responsive shell |

### Sprint 5 (Weeks 10-11): Scan Interface + Results

| Task | Details |
|------|---------|
| Scan page | Text input + image upload + drag-and-drop |
| Results page | Risk score visualization, evidence breakdown, action checklist |
| Loading states | Skeleton UI, progress indicators during scan |
| Error handling | User-friendly error messages, retry logic |
| Scam card page (public) | SSR page with OG tags, social sharing buttons |
| Share flow | Copy link, share to WhatsApp/Twitter/Facebook |

### Sprint 6 (Weeks 12-13): Dashboard + Polish

| Task | Details |
|------|---------|
| User dashboard | Overview: total scans, scams detected, recent activity |
| Scan history | Paginated list of past scans with filters |
| Feedback flow | "Was this helpful?" + "Report false positive" UI |
| SEO | Meta tags, sitemap, robots.txt for scam card pages |
| Performance | Core Web Vitals optimization (LCP < 1.5s) |
| Accessibility | WCAG 2.1 AA compliance |
| E2E tests | Playwright tests for critical flows |
| Deployment | Vercel deployment, staging + production |

**MVP 2 exit criteria**: See [MVP_SCOPE.md](MVP_SCOPE.md) success criteria.

---

## Phase 3 — MVP 3: Mobile + Monetization (Weeks 14-21)

### Sprint 7-8 (Weeks 14-17): React Native App

| Task | Details |
|------|---------|
| Expo project setup | React Native with Expo SDK |
| Auth flow | Login/signup screens, biometric support |
| Scan flow | Text input + camera capture + image picker |
| Results display | Native risk visualization, action list |
| Share sheet receiver | Accept shared text/images from other apps |
| Scam card viewer | Native card display with share functionality |
| Push notifications | Expo Push + backend notification service |
| Offline support | Cache viewed cards, queue scans for later |

### Sprint 9-10 (Weeks 18-21): Payments + Bots + Extension

| Task | Details |
|------|---------|
| Premium tier backend | Plan management, feature gating |
| Stripe integration | International payments, subscription management |
| Razorpay integration | India payments (UPI, cards, netbanking) |
| WhatsApp bot | WhatsApp Business API integration |
| Telegram bot | Telegram Bot API integration |
| Browser extension | Chrome + Firefox, right-click "Check with Savdhaan AI" |
| Admin panel | Internal dashboard for trends, moderation, user management |
| Multi-language UI | Hindi, Tamil, Telugu, Bengali + English |
| App Store submission | iOS App Store + Google Play Store |

**MVP 3 exit criteria**: See [MVP_SCOPE.md](MVP_SCOPE.md) success criteria.

---

## Post-MVP Roadmap

| Quarter | Feature | Description |
|---------|---------|-------------|
| Q3 2026 | Scam clustering | Embeddings-based similarity to detect scam campaigns |
| Q3 2026 | Community reports | User-submitted scam database with verification |
| Q4 2026 | B2B API | White-label scam detection for banks/fintech |
| Q4 2026 | Regional intel | India-specific: UPI fraud DB, TRAI integration |
| Q1 2027 | Real-time protection | Accessibility service / SMS filter for live blocking |
| Q1 2027 | Voice scam detection | Call recording analysis (with consent) |
| Q2 2027 | Scam education | Interactive guides, gamification |

---

## Key Milestones

| Date | Milestone | What it means |
|------|-----------|--------------|
| End of Week 1 | **Dev environment ready** | `make dev` works, CI passes |
| End of Week 7 | **MVP 1 complete** | API is live, scan pipeline works end-to-end |
| End of Week 7 | **Alpha launch** | Invite-only API access for early testers |
| End of Week 13 | **MVP 2 complete** | Web app is live, users can scan and share |
| End of Week 13 | **Beta launch** | Public web app, free tier, feedback collection |
| End of Week 21 | **MVP 3 complete** | Mobile apps published, premium tier live |
| End of Week 21 | **GA launch** | Full public launch across all channels |

---

## Risk Register

| Risk | Impact | Mitigation |
|------|--------|------------|
| Claude API latency spikes | Scan times exceed 3s target | Response caching, two-tier model strategy, timeout + partial results |
| Threat intel source goes down | Missing evidence signals | Graceful degradation, multiple sources, cached results |
| High false positive rate | User trust erosion | Feedback loop, continuous prompt tuning, confidence thresholds |
| Rate limit abuse | Service degradation | Multi-layer rate limiting (API key + IP), abuse detection |
| PII data breach | Legal + trust disaster | Minimal retention, encryption at rest, no PII in logs |
| App store rejection | Mobile launch delay | Follow guidelines strictly, have web fallback |
| LLM cost explosion | Budget overrun | Sonnet-first strategy, caching, rate limits, cost monitoring |
