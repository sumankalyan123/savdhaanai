# Savdhaan AI — Database Schema

> Last updated: 2026-02-20

---

## Overview

Primary database: **PostgreSQL 16**

All tables follow these conventions:
- `id`: UUID primary key (generated via `gen_random_uuid()`)
- `created_at`: TIMESTAMPTZ, default `now()`, NOT NULL
- `updated_at`: TIMESTAMPTZ, auto-updated on modification
- Soft delete via `deleted_at` TIMESTAMPTZ where applicable
- All foreign keys indexed
- All timestamps in UTC

---

## Entity Relationship Diagram

```
┌─────────────┐       ┌──────────────┐       ┌────────────────┐
│   api_keys  │       │    scans     │       │  scan_entities │
├─────────────┤       ├──────────────┤       ├────────────────┤
│ id (PK)     │──┐    │ id (PK)      │──────▶│ id (PK)        │
│ user_id(FK) │  │    │ api_key_id   │       │ scan_id (FK)   │
│ key_hash    │  ├───▶│ content_hash │       │ entity_type    │
│ tier        │  │    │ content_type │       │ entity_value   │
│ is_active   │  │    │ channel      │       │ metadata       │
│ last_used_at│  │    │ locale       │       └────────────────┘
│ created_at  │  │    │ risk_score   │
│ expires_at  │  │    │ risk_level   │       ┌────────────────────┐
└─────────────┘  │    │ scam_type    │       │  threat_results    │
                 │    │ explanation  │       ├────────────────────┤
┌─────────────┐  │    │ actions      │──────▶│ id (PK)            │
│   users     │  │    │ evidence     │       │ scan_id (FK)       │
├─────────────┤  │    │ proc_time_ms │       │ entity_id (FK)     │
│ id (PK)     │──┘    │ model_used   │       │ source             │
│ email       │       │ raw_expired  │       │ result             │
│ tier        │       │ created_at   │       │ is_flagged         │
│ is_active   │       │ updated_at   │       │ raw_response       │
│ created_at  │       │ deleted_at   │       │ checked_at         │
│ updated_at  │       └──────┬───────┘       └────────────────────┘
└─────────────┘              │
                             │               ┌────────────────────┐
                             │               │    scam_cards      │
                             ├──────────────▶├────────────────────┤
                             │               │ id (PK)            │
                             │               │ scan_id (FK)       │
                             │               │ short_code (UQ)    │
                             │               │ summary            │
                             │               │ evidence_summary   │
                             │               │ actions_summary    │
                             │               │ risk_level         │
                             │               │ risk_score         │
                             │               │ scam_type          │
                             │               │ channel            │
                             │               │ image_url          │
                             │               │ view_count         │
                             │               │ share_count        │
                             │               │ created_at         │
                             │               └────────────────────┘
                             │
                             │               ┌────────────────────┐
                             └──────────────▶│    reports         │
                                             ├────────────────────┤
                                             │ id (PK)            │
                                             │ scan_id (FK)       │
                                             │ api_key_id (FK)    │
                                             │ feedback_type      │
                                             │ comment            │
                                             │ status             │
                                             │ created_at         │
                                             └────────────────────┘
```

---

## Table Definitions

### `users`

User accounts (MVP 2+, but schema defined now for FK readiness).

```sql
CREATE TABLE users (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email           VARCHAR(320) UNIQUE,
    password_hash   VARCHAR(255),
    display_name    VARCHAR(100),
    tier            VARCHAR(20) NOT NULL DEFAULT 'free',     -- free, premium, enterprise
    is_active       BOOLEAN NOT NULL DEFAULT true,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    deleted_at      TIMESTAMPTZ
);

CREATE INDEX idx_users_email ON users (email) WHERE deleted_at IS NULL;
CREATE INDEX idx_users_tier ON users (tier) WHERE is_active = true;
```

### `api_keys`

API keys for authentication. Keys are hashed (bcrypt) — never stored in plaintext.

```sql
CREATE TABLE api_keys (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID REFERENCES users(id),
    key_prefix      VARCHAR(12) NOT NULL,                    -- first 12 chars for identification (svd_abc1xxxx)
    key_hash        VARCHAR(255) NOT NULL,                   -- bcrypt hash of full key
    label           VARCHAR(100),                            -- user-defined label
    tier            VARCHAR(20) NOT NULL DEFAULT 'free',
    is_active       BOOLEAN NOT NULL DEFAULT true,
    last_used_at    TIMESTAMPTZ,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    expires_at      TIMESTAMPTZ
);

CREATE INDEX idx_api_keys_prefix ON api_keys (key_prefix) WHERE is_active = true;
CREATE INDEX idx_api_keys_user ON api_keys (user_id);
```

### `scans`

Core scan results. Raw content is NOT stored — only the analysis output.

```sql
CREATE TABLE scans (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    api_key_id      UUID NOT NULL REFERENCES api_keys(id),
    content_hash    VARCHAR(64) NOT NULL,                    -- SHA-256 of input (for dedup, not reconstruction)
    content_type    VARCHAR(10) NOT NULL,                    -- text, image
    channel         VARCHAR(20),                             -- sms, email, whatsapp, etc.
    locale          VARCHAR(10),                             -- detected or provided language
    ocr_text        TEXT,                                    -- extracted text (if image), cleared after retention
    risk_score      SMALLINT NOT NULL CHECK (risk_score BETWEEN 0 AND 100),
    risk_level      VARCHAR(10) NOT NULL,                    -- safe, low, medium, high, critical
    scam_type       VARCHAR(30) NOT NULL,                    -- from scam taxonomy
    explanation     TEXT NOT NULL,                           -- LLM-generated explanation
    evidence        JSONB NOT NULL DEFAULT '[]',             -- array of evidence objects
    actions         JSONB NOT NULL DEFAULT '[]',             -- array of action objects
    entities_found  JSONB NOT NULL DEFAULT '{}',             -- extracted entities summary
    model_used      VARCHAR(50) NOT NULL,                    -- claude-sonnet-4-6, claude-opus-4-6
    processing_time_ms INTEGER NOT NULL,
    raw_expired_at  TIMESTAMPTZ,                             -- when raw content was cleared
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    deleted_at      TIMESTAMPTZ
);

CREATE INDEX idx_scans_api_key ON scans (api_key_id);
CREATE INDEX idx_scans_created ON scans (created_at DESC);
CREATE INDEX idx_scans_scam_type ON scans (scam_type) WHERE deleted_at IS NULL;
CREATE INDEX idx_scans_risk_level ON scans (risk_level) WHERE deleted_at IS NULL;
CREATE INDEX idx_scans_content_hash ON scans (content_hash);
```

### `scan_entities`

Individual entities extracted from scanned content.

```sql
CREATE TABLE scan_entities (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    scan_id         UUID NOT NULL REFERENCES scans(id) ON DELETE CASCADE,
    entity_type     VARCHAR(20) NOT NULL,                    -- url, phone, email, crypto, upi
    entity_value    VARCHAR(2048) NOT NULL,                  -- the extracted entity
    normalized      VARCHAR(2048),                           -- normalized form (e.g., expanded short URL)
    metadata        JSONB DEFAULT '{}',                      -- additional context
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_scan_entities_scan ON scan_entities (scan_id);
CREATE INDEX idx_scan_entities_type ON scan_entities (entity_type);
CREATE INDEX idx_scan_entities_value ON scan_entities (entity_value);
```

### `threat_results`

Results from individual threat intelligence source checks.

```sql
CREATE TABLE threat_results (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    scan_id         UUID NOT NULL REFERENCES scans(id) ON DELETE CASCADE,
    entity_id       UUID NOT NULL REFERENCES scan_entities(id) ON DELETE CASCADE,
    source          VARCHAR(30) NOT NULL,                    -- phishtank, safe_browsing, urlhaus, spamhaus, whois
    is_flagged      BOOLEAN NOT NULL DEFAULT false,
    result          JSONB NOT NULL DEFAULT '{}',             -- source-specific result data
    raw_response    JSONB,                                   -- full API response (for debugging, auto-expires)
    response_time_ms INTEGER,
    checked_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_threat_results_scan ON threat_results (scan_id);
CREATE INDEX idx_threat_results_entity ON threat_results (entity_id);
CREATE INDEX idx_threat_results_source ON threat_results (source);
CREATE INDEX idx_threat_results_flagged ON threat_results (is_flagged) WHERE is_flagged = true;
```

### `scam_cards`

Shareable scam detection summary cards.

```sql
CREATE TABLE scam_cards (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    scan_id         UUID NOT NULL REFERENCES scans(id),
    short_code      VARCHAR(12) UNIQUE NOT NULL,             -- short URL identifier (e.g., abc123)
    summary         TEXT NOT NULL,                           -- one-line summary for sharing
    evidence_summary JSONB NOT NULL DEFAULT '[]',            -- simplified evidence bullets
    actions_summary JSONB NOT NULL DEFAULT '[]',             -- simplified action bullets
    risk_level      VARCHAR(10) NOT NULL,
    risk_score      SMALLINT NOT NULL,
    scam_type       VARCHAR(30) NOT NULL,
    channel         VARCHAR(20),
    image_url       VARCHAR(500),                            -- S3/CDN URL for card image
    image_generated BOOLEAN NOT NULL DEFAULT false,
    view_count      INTEGER NOT NULL DEFAULT 0,
    share_count     INTEGER NOT NULL DEFAULT 0,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_scam_cards_short_code ON scam_cards (short_code);
CREATE INDEX idx_scam_cards_scan ON scam_cards (scan_id);
CREATE INDEX idx_scam_cards_created ON scam_cards (created_at DESC);
```

### `reports`

User feedback on scan accuracy.

```sql
CREATE TABLE reports (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    scan_id         UUID NOT NULL REFERENCES scans(id),
    api_key_id      UUID NOT NULL REFERENCES api_keys(id),
    feedback_type   VARCHAR(20) NOT NULL,                    -- confirm_scam, false_positive, not_sure, additional_info
    comment         VARCHAR(500),
    status          VARCHAR(20) NOT NULL DEFAULT 'received', -- received, reviewed, actioned
    reviewed_at     TIMESTAMPTZ,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_reports_scan ON reports (scan_id);
CREATE INDEX idx_reports_type ON reports (feedback_type);
CREATE INDEX idx_reports_status ON reports (status) WHERE status != 'actioned';
```

---

## Anti-Abuse Tables

### `abuse_events`

Individual abuse signals captured per API key per scan.

```sql
CREATE TABLE abuse_events (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    api_key_id      UUID NOT NULL REFERENCES api_keys(id),
    scan_id         UUID REFERENCES scans(id),
    event_type      VARCHAR(30) NOT NULL,                    -- high_frequency, iterative_testing, high_flag_rate,
                                                             -- entity_reuse, burst_pattern, rapid_account
    details         JSONB DEFAULT '{}',                      -- event-specific context
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_abuse_events_api_key ON abuse_events (api_key_id);
CREATE INDEX idx_abuse_events_created ON abuse_events (created_at DESC);
CREATE INDEX idx_abuse_events_type ON abuse_events (event_type);
```

### `abuse_scores`

Rolling abuse score per API key. Updated on every scan. Drives response degradation.

```sql
CREATE TABLE abuse_scores (
    api_key_id      UUID PRIMARY KEY REFERENCES api_keys(id),
    score           SMALLINT NOT NULL DEFAULT 0 CHECK (score BETWEEN 0 AND 100),
    scan_count_1h   INTEGER NOT NULL DEFAULT 0,              -- scans in last hour
    flagged_ratio   REAL NOT NULL DEFAULT 0.0,               -- ratio of flagged scans (0.0-1.0)
    similarity_ratio REAL NOT NULL DEFAULT 0.0,              -- ratio of semantically similar scans
    entity_reuse_ratio REAL NOT NULL DEFAULT 0.0,            -- ratio of reused entities
    response_level  VARCHAR(10) NOT NULL DEFAULT 'full',     -- full, reduced, minimal, throttled
    is_flagged      BOOLEAN NOT NULL DEFAULT false,          -- flagged for manual review
    flagged_at      TIMESTAMPTZ,
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_abuse_scores_flagged ON abuse_scores (is_flagged) WHERE is_flagged = true;
CREATE INDEX idx_abuse_scores_level ON abuse_scores (response_level) WHERE response_level != 'full';
```

### `semantic_fingerprints`

Stores semantic fingerprints of scanned content to detect iterative testing
(same scam template with minor variations across any account).

```sql
CREATE TABLE semantic_fingerprints (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    fingerprint     VARCHAR(64) NOT NULL,                    -- SimHash/MinHash of message structure
    scan_id         UUID NOT NULL REFERENCES scans(id),
    api_key_id      UUID NOT NULL REFERENCES api_keys(id),
    scam_type       VARCHAR(30),
    risk_level      VARCHAR(10),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_fingerprints_hash ON semantic_fingerprints (fingerprint);
CREATE INDEX idx_fingerprints_api_key ON semantic_fingerprints (api_key_id);
CREATE INDEX idx_fingerprints_created ON semantic_fingerprints (created_at DESC);
```

**How fingerprints work**: When the same semantic fingerprint appears across multiple
API keys with slight content variations (and most scans are flagged), that pattern is
boosted in detection confidence for all users. Scammer testing strengthens our detection.

---

## Audit Log Table

Immutable, append-only audit trail for all security-relevant actions.
See [SECURITY.md](SECURITY.md) for full audit logging strategy.

```sql
CREATE TABLE audit_logs (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_type      VARCHAR(50) NOT NULL,                    -- auth_success, auth_failure, key_created, key_revoked,
                                                             -- scan_performed, rate_limit_hit, abuse_flagged,
                                                             -- data_deletion, admin_action, config_change
    actor_type      VARCHAR(20) NOT NULL,                    -- user, api_key, system, admin
    actor_id        VARCHAR(100),                            -- user UUID, key prefix, "system"
    target_type     VARCHAR(30),                             -- scan, api_key, user, config
    target_id       VARCHAR(100),
    action          VARCHAR(50) NOT NULL,                    -- created, revoked, accessed, modified, deleted
    details         JSONB DEFAULT '{}',                      -- event-specific context (NO PII)
    ip_address      INET,
    user_agent      VARCHAR(500),
    request_id      UUID,                                    -- correlation ID
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- IMPORTANT: Application DB user has INSERT-only privilege on this table.
-- No UPDATE or DELETE allowed — enforced at database role level.

CREATE INDEX idx_audit_event_type ON audit_logs (event_type);
CREATE INDEX idx_audit_actor ON audit_logs (actor_type, actor_id);
CREATE INDEX idx_audit_target ON audit_logs (target_type, target_id);
CREATE INDEX idx_audit_created ON audit_logs (created_at DESC);
```

---

## Scam Taxonomy Reference Table

Static reference data — seeded via script, rarely changes.

```sql
CREATE TABLE scam_types (
    code            VARCHAR(30) PRIMARY KEY,                 -- phishing, smishing, advance_fee, etc.
    label           VARCHAR(100) NOT NULL,                   -- Human-readable name
    description     TEXT NOT NULL,                           -- What this scam type means
    severity_hint   VARCHAR(10) NOT NULL DEFAULT 'high',     -- typical severity: low, medium, high, critical
    examples        JSONB DEFAULT '[]',                      -- example phrases/patterns
    is_active       BOOLEAN NOT NULL DEFAULT true,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

---

## Data Retention

| Data | Retention | Mechanism |
|------|-----------|-----------|
| Raw message content (ocr_text) | 1 hour (configurable) | Celery periodic task nullifies field |
| Threat intel raw_response | 24 hours | Celery periodic task nullifies field |
| Scan results (classification, evidence) | Indefinite | User can request deletion |
| Scam cards | Indefinite | Public resource |
| User reports | Indefinite | Used for model improvement |
| API key hashes | Until key revoked | Hard delete on revocation |

---

## Migration Strategy

- All schema changes via **Alembic** — never modify DB directly
- Migration files are version-controlled and code-reviewed
- Naming convention: `YYYY_MM_DD_HHMM_description.py`
- Destructive migrations require explicit confirmation in CI/CD
- Rollback scripts included for every migration
