# Savdhaan AI — MVP Scope Definition

> Last updated: 2026-02-20

---

## Vision

Savdhaan AI is a cross-channel scam detection copilot that helps users detect, understand,
and respond to scams across SMS, email, WhatsApp, social DMs, and any text/image-based content.
It produces explainable, evidence-grounded risk assessments and shareable "scam cards" to warn others.

---

## MVP 1 — Core Scan Pipeline + API (Backend-Only)

**Goal**: A fully functional, API-first scam detection engine that can be consumed by any client.

**Timeline target**: 6-8 weeks

### In Scope

| Feature | Description | Priority |
|---------|-------------|----------|
| **Text scan** | Accept raw text (SMS, email body, chat message) and return a risk assessment | P0 |
| **Image scan** | Accept screenshot upload, run OCR, then same pipeline as text scan | P0 |
| **Entity extraction** | LLM-based extraction of URLs, phone numbers, emails, crypto wallets, UPI IDs | P0 |
| **Threat intelligence** | Parallel checks against PhishTank, Google Safe Browsing, URLhaus, Spamhaus, WHOIS | P0 |
| **LLM classification** | Scam type detection with risk score (0-100) and evidence-grounded explanation | P0 |
| **Action recommendations** | Context-aware recommended actions per scam type and risk level | P0 |
| **Scam card generation** | Shareable summary card with unique URL and Open Graph tags for rich previews | P1 |
| **User reports / feedback** | Submit "this was a scam" or "false positive" feedback on any scan | P1 |
| **Rate limiting** | Token-bucket rate limiting: 10 scans/hour (free), 100 scans/hour (premium) | P0 |
| **API key auth** | API key-based authentication for programmatic access | P0 |
| **Health + metrics** | `/health` endpoint, Prometheus metrics, structured JSON logging | P1 |
| **OpenAPI docs** | Auto-generated interactive API docs (Swagger UI + ReDoc) | P0 |
| **Anti-abuse detection** | Behavioral scoring to detect scammers testing messages, progressive response degradation | P1 |
| **Honest messaging** | Results always state what was checked and what couldn't be checked, no absolute safety claims | P0 |

### Out of Scope (MVP 1)

- Web frontend / mobile app
- User registration / login (email/password or OAuth)
- Scan history / dashboard
- Premium billing / payments
- Browser extension
- WhatsApp bot / Telegram bot
- Push notifications
- Scam similarity clustering / embeddings
- Multi-language UI (API supports multi-language content via LLM)
- Admin panel

### Success Criteria

- [ ] End-to-end text scan completes in < 3 seconds (p95)
- [ ] End-to-end image scan completes in < 5 seconds (p95)
- [ ] Threat intel checks run in parallel, with graceful degradation if any source is down
- [ ] LLM classification produces structured output with cited evidence for every result
- [ ] Scam card URLs render rich previews when shared on WhatsApp / iMessage / Twitter
- [ ] API handles 100 concurrent requests without degradation
- [ ] Test coverage >= 80% on `services/` layer
- [ ] Zero PII logged or persisted beyond processing window
- [ ] Abuse detection flags iterative testing patterns (>70% similar content from same key)
- [ ] No scan result ever uses absolute language ("safe", "guaranteed", "definitely")

### Deliverables

1. Dockerized FastAPI application with all scan pipeline services
2. PostgreSQL schema with Alembic migrations
3. Redis-backed rate limiting and caching
4. Celery workers for background threat intel
5. Comprehensive test suite with fixtures
6. OpenAPI spec + interactive docs
7. `.env.example`, Makefile, docker-compose for local dev
8. Seed script for scam taxonomy reference data
9. Anti-abuse scoring service with progressive response degradation
10. Honest messaging framework — all responses qualify confidence and state limitations

---

## MVP 2 — Web App + User Accounts

**Goal**: A consumer-facing web application where users can scan content, view history,
and share scam cards — with full authentication.

**Timeline target**: 4-6 weeks after MVP 1

### In Scope

| Feature | Description | Priority |
|---------|-------------|----------|
| **Next.js web app** | Server-rendered web application with responsive design | P0 |
| **Auth system** | Email/password signup + Google/Apple OAuth via NextAuth.js | P0 |
| **Scan page** | Text input + image upload with real-time results | P0 |
| **Results page** | Risk score visualization, evidence breakdown, action checklist | P0 |
| **Scam card page** | Public shareable page with OG tags, optimized for social/messaging sharing | P0 |
| **Scan history** | Authenticated users can view past scans | P1 |
| **User dashboard** | Overview: total scans, scams detected, cards shared | P1 |
| **Feedback flow** | "Was this helpful?" + "Report false positive" in results UI | P1 |
| **SEO** | Server-rendered scam card pages indexed by search engines | P1 |
| **Analytics** | Basic product analytics (scans per day, scam types distribution) | P2 |
| **Responsive design** | Mobile-first, works on all screen sizes | P0 |

### Out of Scope (MVP 2)

- Native mobile app
- Premium billing / payments
- Browser extension
- Bot integrations (WhatsApp, Telegram)
- Admin panel
- Multi-language UI
- Push notifications

### Success Criteria

- [ ] Scan-to-result flow completes in < 4 seconds (including UI rendering)
- [ ] Scam card pages load in < 1.5 seconds (Core Web Vitals: LCP)
- [ ] Authentication works with email + at least one OAuth provider
- [ ] Mobile responsive — fully usable on 375px viewport
- [ ] Lighthouse score > 90 on performance, accessibility, SEO

### Deliverables

1. Next.js 15 application deployed on Vercel or similar
2. Auth system with session management
3. Scan interface (text + image)
4. Results display with evidence visualization
5. Public scam card pages with Open Graph + Twitter Card meta
6. User dashboard with scan history
7. E2E tests with Playwright

---

## MVP 3 — Mobile App + Monetization + Integrations

**Goal**: Native mobile experience, premium tier with payments, and messaging platform
integrations for maximum reach.

**Timeline target**: 6-8 weeks after MVP 2

### In Scope

| Feature | Description | Priority |
|---------|-------------|----------|
| **React Native app** | iOS + Android via Expo | P0 |
| **Share sheet** | Forward messages from any app directly to Savdhaan AI | P0 |
| **Camera scan** | Photograph suspicious content, auto-OCR | P0 |
| **Push notifications** | Trending scam alerts by region | P1 |
| **Premium tier** | Stripe/Razorpay billing: higher rate limits, scan history, priority processing | P0 |
| **WhatsApp bot** | Forward message to Savdhaan AI WhatsApp number, get scam card back | P1 |
| **Telegram bot** | Same flow as WhatsApp | P2 |
| **Browser extension** | Right-click "Check with Savdhaan AI" on any text/image | P1 |
| **Admin panel** | Internal dashboard for scam trends, user management, moderation | P1 |
| **Multi-language UI** | Hindi, Tamil, Telugu, Bengali (top Indian languages) + English | P1 |
| **Offline cards** | Cache viewed scam cards for offline access on mobile | P2 |

### Out of Scope (MVP 3)

- Voice call scam detection
- Video content analysis
- Real-time interception / auto-block
- White-label / B2B API
- Community features (forums, user-submitted scam reports)

### Success Criteria

- [ ] Mobile app published on App Store + Google Play
- [ ] Share sheet works from WhatsApp, SMS, Email, and social apps
- [ ] Payment flow works for India (Razorpay) and international (Stripe)
- [ ] WhatsApp bot responds within 5 seconds
- [ ] App startup time < 2 seconds
- [ ] Push notification delivery rate > 95%

### Deliverables

1. React Native (Expo) app on both stores
2. Payment integration (Stripe + Razorpay)
3. WhatsApp Business API integration
4. Telegram bot
5. Chrome/Firefox browser extension
6. Admin panel (can be simple — Next.js admin routes or Retool)
7. Localization for 5+ languages
8. Mobile-specific test suite

---

## Future (Post-MVP 3)

| Feature | Description |
|---------|-------------|
| **Scam similarity clustering** | Embeddings-based clustering to detect scam campaigns |
| **Community scam reports** | User-submitted scam database with voting/verification |
| **B2B API** | White-label scam detection for banks, telecom, fintech |
| **Real-time protection** | Accessibility service / SMS filter for live protection |
| **Voice scam detection** | Analyze call recordings (with consent) |
| **Regional threat intelligence** | India-specific: UPI fraud DB, TRAI DND, Cyber Crime Portal integration |
| **Scam education** | Interactive guides on common scam types by region |
| **Gamification** | Badges, streaks for checking suspicious messages |

---

## Scam Taxonomy (MVP 1 Classification Categories)

The LLM classifier will categorize scams into these types:

| Category | Examples |
|----------|---------|
| `phishing` | Fake login pages, credential harvesting, "verify your account" |
| `smishing` | SMS-based phishing with malicious links |
| `vishing_setup` | Text directing to call a fake support number |
| `advance_fee` | Nigerian prince, lottery winning, inheritance scams |
| `tech_support` | Fake virus alerts, "your computer is infected" |
| `impersonation` | Fake bank, government, delivery service messages |
| `investment` | Crypto pump-and-dump, forex scams, Ponzi scheme recruitment |
| `romance` | Relationship-building leading to money requests |
| `job_scam` | Fake job offers requiring upfront payment or personal info |
| `shopping` | Fake e-commerce, too-good-to-be-true deals |
| `upi_fraud` | India-specific: fake UPI collect requests, QR code scams |
| `loan_scam` | Fake instant loan apps, predatory lending |
| `customs_tax` | Fake customs duty / tax payment demands |
| `prize_lottery` | "You've won!" messages requiring payment to claim |
| `charity` | Fake charitable organizations, disaster relief scams |
| `subscription_trap` | Free trial → hidden recurring charges |
| `safe` | Legitimate message, no scam detected |
| `suspicious` | Not clearly a scam, but exhibits some warning signs |

### Risk Levels

| Level | Score Range | Meaning |
|-------|------------|---------|
| `critical` | 80-100 | Known scam pattern, confirmed malicious indicators |
| `high` | 60-79 | Strong scam signals, multiple red flags |
| `medium` | 40-59 | Some suspicious elements, exercise caution |
| `low` | 20-39 | Minor concerns, likely legitimate |
| `safe` | 0-19 | No scam indicators detected |
