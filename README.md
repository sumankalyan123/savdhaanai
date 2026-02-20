# Savdhaan AI

**AI risk copilot that helps people make safer decisions — starting with scam detection.**

> सावधान (Savdhaan) = Be alert. Be cautious. Be aware.

## What is Savdhaan AI?

Paste a suspicious message, screenshot, or email — get an instant, evidence-based risk assessment with a shareable warning card.

**Phase 1**: Scam detection (SMS, email, WhatsApp, social DMs, UPI requests)
**Phase 2+**: Job offers, rental leases, investment pitches, contracts

## Tech Stack

- **Backend**: Python 3.12+ / FastAPI / SQLAlchemy 2.0 / Celery
- **AI**: Anthropic Claude API (structured tool_use)
- **Threat Intel**: PhishTank, Google Safe Browsing, URLhaus, Spamhaus, WHOIS
- **Database**: PostgreSQL 16 + Redis 7
- **Infrastructure**: Docker / Kubernetes / AWS

## Documentation

All detailed docs live in [`docs/`](docs/):

| Doc | What it covers |
|-----|---------------|
| [PRODUCT_VISION.md](docs/PRODUCT_VISION.md) | Full product vision, strategy, revenue model |
| [MVP_SCOPE.md](docs/MVP_SCOPE.md) | MVP 1/2/3 scope, success criteria, scam taxonomy |
| [ARCHITECTURE.md](docs/ARCHITECTURE.md) | System architecture, tech rationale, security model |
| [API_DESIGN.md](docs/API_DESIGN.md) | All endpoints, schemas, error codes |
| [DATABASE_SCHEMA.md](docs/DATABASE_SCHEMA.md) | Table definitions, ERD, indexes |
| [THREAT_INTEL.md](docs/THREAT_INTEL.md) | Threat intel sources, integration details |
| [SECURITY.md](docs/SECURITY.md) | Auth, encryption, RBAC, compliance, incident response |
| [DEPLOYMENT.md](docs/DEPLOYMENT.md) | AWS hosting, Docker, K8s, CI/CD, monitoring |
| [ROADMAP.md](docs/ROADMAP.md) | Sprint plan, milestones, risk register |
| [LIMITATIONS.md](docs/LIMITATIONS.md) | Honest limitations, anti-abuse strategy |

## Status

**Phase 0 + MVP 1 Sprints 1-3 — COMPLETE** (2026-02-20)

All core backend code is built: scan pipeline, API endpoints, database models, threat intel integrations, LLM classifier, scam card generator, and 30 passing tests.

See [docs/PROGRESS.md](docs/PROGRESS.md) for detailed build progress and what's next.

### Quick Start

```bash
# 1. Clone and install
git clone https://github.com/sumankalyan123/savdhaanai.git
cd savdhaanai
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"

# 2. Copy env and add your API keys
cp .env.example .env

# 3. Run tests
make test

# 4. Start local dev (Docker required)
make dev

# 5. Run migrations + seed
make migrate
make seed
```

## License

Proprietary. All rights reserved.
