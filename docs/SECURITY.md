# Savdhaan AI — Security, Authentication & Governance

> Last updated: 2026-02-20

---

## Security Principles

1. **Defense in depth** — Multiple layers, no single point of failure
2. **Least privilege** — Every component gets minimum required access
3. **Secure by default** — Safe configuration out of the box, opt-in to less secure options
4. **Assume breach** — Design so a compromised component can't take down everything
5. **Privacy first** — Collect minimum data, retain briefly, delete aggressively

---

## Authentication

### MVP 1 — API Key Authentication

API keys are the sole auth mechanism for MVP 1. Designed for developer/programmatic access.

**Key format**: `svd_` prefix + 32-char random alphanumeric string
```
svd_a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6
```

**Key lifecycle**:
```
Generate key → Show ONCE to user → Store bcrypt hash in DB → Never retrievable again
```

**Storage**:
- Full key shown to user exactly once at creation time
- `key_prefix` (first 12 chars: `svd_a1b2c3d4`) stored in plaintext for identification
- `key_hash` stored as bcrypt hash (cost factor 12)
- Original key is never stored and cannot be recovered

**Validation flow**:
```
Request with X-API-Key header
        │
        ▼
Extract prefix (first 12 chars)
        │
        ▼
Query api_keys WHERE key_prefix = ? AND is_active = true AND (expires_at IS NULL OR expires_at > now())
        │
        ▼
bcrypt.verify(provided_key, stored_hash)
        │
        ├── Match → Load tier, update last_used_at, proceed
        └── No match → 401 Unauthorized
```

**Security controls**:
- Keys can be revoked instantly (set `is_active = false`)
- Keys support optional expiration (`expires_at`)
- Users can have multiple keys (e.g., separate keys for test/prod)
- Key creation and revocation are logged in audit trail
- Brute force protection: rate limit auth failures by IP (5 failures → 15 min lockout)

### MVP 2+ — JWT + OAuth

**JWT tokens** for web/mobile sessions. **API keys** remain for programmatic access.

**Auth providers** (via NextAuth.js / Auth.js v5):

| Provider | Market | Details |
|----------|--------|---------|
| Email + password | All | Bcrypt-hashed passwords, email verification required |
| Google OAuth | All | OpenID Connect, standard scopes (profile, email) |
| Apple Sign-In | iOS users | Required for App Store compliance |

**JWT design**:
```json
{
  "sub": "user-uuid",
  "email": "user@example.com",
  "tier": "premium",
  "iat": 1708423200,
  "exp": 1708426800,
  "jti": "unique-token-id"
}
```

| Property | Value | Rationale |
|----------|-------|-----------|
| Algorithm | ES256 (ECDSA P-256) | Asymmetric — API servers only need public key to verify |
| Access token TTL | 15 minutes | Short-lived, limits damage if stolen |
| Refresh token TTL | 7 days | Stored as httpOnly secure cookie |
| Token storage (web) | httpOnly, Secure, SameSite=Strict cookie | Not accessible via JavaScript, XSS-proof |
| Token storage (mobile) | Secure Keychain (iOS) / EncryptedSharedPreferences (Android) | Platform-native secure storage |
| Refresh rotation | Yes — each refresh issues new refresh token, old one invalidated | Limits replay window |

**OAuth security**:
- PKCE (Proof Key for Code Exchange) required for all OAuth flows (mobile and web)
- State parameter with CSRF token for web OAuth
- Nonce validation for OpenID Connect
- Redirect URI strictly validated against whitelist
- Token exchange happens server-side only (never in browser)

---

## Authorization — Role-Based Access Control (RBAC)

### User Roles

| Role | Description | Permissions |
|------|-------------|-------------|
| `anonymous` | No account, using shared card links | View public scam cards only |
| `free` | Registered user, free tier | Scan (rate limited), view own history, submit reports |
| `premium` | Paid subscriber | Higher rate limits, all categories, priority processing, full history |
| `enterprise` | B2B API customer | Custom rate limits, SLA, dedicated support, webhooks |
| `admin` | Internal team | All user permissions + admin panel, user management, moderation |
| `super_admin` | Founders / CTO | Admin + infrastructure access, key rotation, audit log access |

### Permission Matrix

| Action | anonymous | free | premium | enterprise | admin |
|--------|-----------|------|---------|------------|-------|
| View public scam card | Y | Y | Y | Y | Y |
| Submit scan | — | Y (10/hr) | Y (100/hr) | Y (1000/hr) | Y |
| View own scan history | — | Y | Y | Y | Y |
| Submit feedback/report | — | Y | Y | Y | Y |
| Delete own data | — | Y | Y | Y | Y |
| Access all categories | — | scam only | all | all | all |
| API key management | — | 1 key | 5 keys | 20 keys | unlimited |
| View admin panel | — | — | — | — | Y |
| Manage users | — | — | — | — | Y |
| View audit logs | — | — | — | — | Y |
| Rotate secrets | — | — | — | — | super only |

### API Key Scoping (Enterprise)

Enterprise API keys can be scoped to specific permissions:
```json
{
  "key_prefix": "svd_ent1xxxx",
  "scopes": ["scan:read", "scan:write", "card:read"],
  "allowed_categories": ["scam_check", "job_offer"],
  "ip_whitelist": ["203.0.113.0/24"],
  "rate_limit_override": 500
}
```

---

## Encryption

### In Transit

| Layer | Protocol | Minimum Version | Details |
|-------|----------|----------------|---------|
| Client → API | TLS | 1.2 (prefer 1.3) | Enforced at load balancer. HSTS header with 1-year max-age. |
| API → Database | TLS | 1.2 | PostgreSQL `sslmode=verify-full`. Client cert auth in production. |
| API → Redis | TLS | 1.2 | Redis 7 native TLS. Required in production, optional in dev. |
| API → External APIs | TLS | 1.2 | httpx with certificate verification enabled (default). |
| Internal services | mTLS | 1.2 | Mutual TLS between API, Celery workers, and other internal services in production. |

**Cipher suites** (TLS 1.3 preferred):
- TLS_AES_256_GCM_SHA384
- TLS_CHACHA20_POLY1305_SHA256
- TLS_AES_128_GCM_SHA256

**Certificate management**:
- Production: AWS Certificate Manager (ACM) or Let's Encrypt via cert-manager on Kubernetes
- Auto-renewal with 30-day pre-expiry rotation
- Certificate transparency monitoring for savdhaan.ai domain

### At Rest

| Data | Encryption | Method |
|------|-----------|--------|
| PostgreSQL | Full-disk encryption | AWS RDS encryption (AES-256) or GCP Cloud SQL encryption. Always on. |
| Redis | In-memory (no disk by default) | ElastiCache at-rest encryption enabled. AOF/RDB backups encrypted. |
| S3 / Object storage | Server-side encryption | SSE-S3 (AES-256) default. SSE-KMS for scam card images. |
| Backups | Encrypted | Same encryption as source. Cross-region backup copies also encrypted. |
| Logs | Encrypted | CloudWatch/ELK storage encryption. No PII in logs regardless. |

### Field-Level Encryption

Some fields get additional application-level encryption before database storage:

| Field | Why | Method |
|-------|-----|--------|
| `api_keys.key_hash` | API key material | bcrypt (not reversible — this is hashing, not encryption) |
| `users.password_hash` | User passwords | bcrypt with cost factor 12 |
| `users.email` (future) | PII if required by DPDP | AES-256-GCM with per-tenant key (envelope encryption) |

### Key Management

| Environment | Key Storage | Details |
|-------------|------------|---------|
| Local dev | `.env` file | Never committed. `.env.example` has placeholder values. |
| CI/CD | GitHub Actions Secrets | Encrypted at rest, masked in logs, scoped per environment. |
| Staging | AWS Secrets Manager or GCP Secret Manager | Versioned, auto-rotated where possible, access-logged. |
| Production | AWS KMS + Secrets Manager (or GCP KMS + Secret Manager) | HSM-backed master keys. Envelope encryption for application secrets. |

**Key rotation schedule**:

| Secret | Rotation frequency | Method |
|--------|-------------------|--------|
| Database credentials | 90 days | Secrets Manager auto-rotation |
| Redis password | 90 days | Secrets Manager auto-rotation |
| API signing keys (JWT) | 180 days | Key pair rotation with grace period (old key valid for 24h after rotation) |
| Anthropic API key | On compromise or annually | Manual rotation with zero-downtime swap |
| Third-party API keys | Annually or on compromise | Manual rotation per provider |

---

## Security Headers

All API responses include:

```
Strict-Transport-Security: max-age=31536000; includeSubDomains; preload
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 0          (deprecated, but set to 0 per modern best practice)
Referrer-Policy: strict-origin-when-cross-origin
Permissions-Policy: camera=(), microphone=(), geolocation=()
Cache-Control: no-store        (for API responses containing scan results)
```

Scam card public pages (server-rendered HTML) additionally include:
```
Content-Security-Policy: default-src 'self'; img-src 'self' https://cdn.savdhaan.ai; style-src 'self' 'unsafe-inline'; script-src 'self'
X-Frame-Options: SAMEORIGIN    (allow embedding scam card previews on savdhaan.ai only)
```

### CORS Policy

```python
CORS_CONFIG = {
    "allow_origins": [
        "https://savdhaan.ai",
        "https://www.savdhaan.ai",
        "https://app.savdhaan.ai",
    ],
    "allow_methods": ["GET", "POST", "OPTIONS"],
    "allow_headers": ["Authorization", "X-API-Key", "Content-Type", "X-Request-Id"],
    "expose_headers": ["X-RateLimit-Limit", "X-RateLimit-Remaining", "X-RateLimit-Reset", "X-Request-Id"],
    "allow_credentials": True,
    "max_age": 3600,
}

# Local dev overrides
if settings.ENVIRONMENT == "development":
    CORS_CONFIG["allow_origins"] = ["http://localhost:3000", "http://localhost:8000"]
```

---

## Audit Logging

### What Gets Logged

Every security-relevant action creates an immutable audit record.

| Event | Logged Fields | Retention |
|-------|--------------|-----------|
| API key created | key_prefix, user_id, tier, created_by | Indefinite |
| API key revoked | key_prefix, user_id, revoked_by, reason | Indefinite |
| Authentication success | key_prefix or user_id, IP, user_agent | 90 days |
| Authentication failure | IP, user_agent, attempted_prefix | 90 days |
| Scan performed | scan_id, api_key_id, category, risk_level (NOT content) | 1 year |
| Rate limit hit | api_key_id, IP, current_count, limit | 30 days |
| Abuse score threshold crossed | api_key_id, old_score, new_score, trigger_event | 1 year |
| Account flagged for review | api_key_id, reason, flagged_by (system/admin) | Indefinite |
| User data deletion request | user_id, requested_at, completed_at | Indefinite (legal) |
| Admin action | admin_user_id, action, target, details | Indefinite |
| Config/secret change | changed_by, what_changed (NOT the value) | Indefinite |

### Audit Log Schema

```sql
CREATE TABLE audit_logs (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_type      VARCHAR(50) NOT NULL,
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

-- Append-only: no UPDATE or DELETE allowed on this table (enforced by DB permissions)
-- Application DB user has INSERT-only privilege on audit_logs

CREATE INDEX idx_audit_event_type ON audit_logs (event_type);
CREATE INDEX idx_audit_actor ON audit_logs (actor_type, actor_id);
CREATE INDEX idx_audit_target ON audit_logs (target_type, target_id);
CREATE INDEX idx_audit_created ON audit_logs (created_at DESC);
```

**Immutability**: The application database user has `INSERT`-only permission on `audit_logs`. No `UPDATE` or `DELETE`. Only the DBA role (used for maintenance, never by the application) can modify audit data.

---

## Compliance

### GDPR (EU — General Data Protection Regulation)

Applicable when serving EU users (UK/expansion market).

| Requirement | How we comply |
|-------------|--------------|
| **Lawful basis** | Legitimate interest (scam detection) + user consent for account creation |
| **Data minimization** | Raw content deleted after 1 hour. Only classification metadata retained. |
| **Purpose limitation** | Data used solely for scam/risk detection and improvement. Never sold. |
| **Storage limitation** | Retention schedule enforced by automated Celery tasks. |
| **Right to access** | `GET /api/v1/user/data` — export all user data as JSON (MVP 2+) |
| **Right to erasure** | `DELETE /api/v1/user/data` — hard delete all user data within 72 hours |
| **Right to rectification** | Users can update profile data via API/UI |
| **Data portability** | Export endpoint provides machine-readable JSON |
| **Breach notification** | 72-hour notification to supervisory authority. See Incident Response below. |
| **DPA (Data Processing Agreement)** | Required for enterprise customers. Template prepared. |
| **DPIA (Data Protection Impact Assessment)** | Completed before launch. Reviewed annually. |
| **Data Protection Officer** | Designated (may be outsourced initially) |

**Cross-border data transfers**: If hosting in US/India and serving EU users, use Standard Contractual Clauses (SCCs) or ensure hosting provider has EU adequacy decision coverage.

### DPDP Act 2023 (India — Digital Personal Data Protection)

Primary market. Mandatory compliance.

| Requirement | How we comply |
|-------------|--------------|
| **Consent** | Clear, specific consent at signup. Granular opt-in for data processing. |
| **Purpose limitation** | Data processed only for stated purpose (scam/risk detection). |
| **Data minimization** | Same as GDPR — minimal collection, aggressive deletion. |
| **Accuracy** | Users can correct their data. Scan results not editable (they're AI outputs). |
| **Storage limitation** | Automated retention policies. Raw content deleted after processing. |
| **Right to erasure** | Same endpoint as GDPR. Full deletion within 72 hours. |
| **Right to nomination** | Users can nominate another person to exercise their rights (in case of death/incapacity). |
| **Grievance redressal** | Dedicated grievance officer. Contact via support@savdhaan.ai. Response within 7 days. |
| **Significant data fiduciary** | If we cross the threshold (user volume), additional obligations apply — annual audit, DPO appointment. |
| **Children's data** | If under 18 detected, require verifiable parental consent or restrict access. |
| **Data localization** | DPDP does not currently mandate data localization, but government can notify categories. Monitor. |

### SOC 2 (Future — B2B Requirement)

Not required for MVP, but design with SOC 2 readiness:

| Trust principle | Current readiness |
|----------------|------------------|
| Security | Strong — encryption, auth, rate limiting, audit logs |
| Availability | Moderate — need SLA targets, monitoring, DR plan |
| Processing integrity | Strong — structured LLM output validation, evidence grounding |
| Confidentiality | Strong — minimal retention, PII handling, encryption |
| Privacy | Strong — GDPR/DPDP compliance, consent management |

**Target**: SOC 2 Type I within 6 months of B2B launch. Type II within 12 months.

---

## Database Security

### Access Control

| Role | Permissions | Used by |
|------|-------------|---------|
| `savdhaan_app` | SELECT, INSERT, UPDATE on application tables. INSERT-only on audit_logs. | FastAPI application |
| `savdhaan_worker` | SELECT, INSERT, UPDATE on scan/threat tables. INSERT on audit_logs. | Celery workers |
| `savdhaan_readonly` | SELECT on all tables | Monitoring, analytics, read replicas |
| `savdhaan_migrate` | ALL on schema (DDL) | Alembic migrations only (CI/CD pipeline) |
| `savdhaan_dba` | SUPERUSER | DBA only, break-glass access, never used by application |

### SQL Injection Prevention

- All queries go through SQLAlchemy ORM — parameterized by default
- Raw SQL (if ever needed) uses bound parameters: `text("SELECT * FROM scans WHERE id = :id").bindparams(id=scan_id)`
- No string concatenation in queries — enforced by linter rule
- Pydantic validates all input before it reaches the ORM

### Row-Level Security (Future)

For multi-tenant enterprise:
```sql
ALTER TABLE scans ENABLE ROW LEVEL SECURITY;

CREATE POLICY scan_isolation ON scans
    USING (api_key_id IN (SELECT id FROM api_keys WHERE user_id = current_setting('app.current_user_id')::uuid));
```

---

## Application Security

### Input Validation

| Input | Validation | Max Size |
|-------|-----------|----------|
| Text content | UTF-8 string, stripped of null bytes | 50,000 characters |
| Image upload | Validated MIME type (JPEG, PNG, WebP, HEIC), magic bytes check | 10 MB |
| API key | Regex: `^sk_(live|test)_[a-zA-Z0-9]{32}$` | Fixed 44 chars |
| URL in content | Validated format, resolved for redirects (max 5 hops) | 2,048 chars |
| User comment (reports) | UTF-8, HTML-stripped | 500 chars |
| Email | RFC 5322 validation | 320 chars |
| UUID parameters | Strict UUID v4 format validation | Fixed 36 chars |

### Output Sanitization

- All LLM output is validated against expected Pydantic schemas before inclusion in API response
- No raw LLM text reaches the user without schema validation
- HTML in LLM output is stripped (not escaped — stripped entirely)
- JSON responses are serialized with `ensure_ascii=False` but no executable content

### File Upload Security

```python
ALLOWED_MIME_TYPES = {"image/jpeg", "image/png", "image/webp", "image/heic"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
MAX_IMAGE_DIMENSIONS = (4096, 4096)  # pixels

# Validation sequence:
# 1. Check Content-Type header
# 2. Read first 8 bytes — verify magic bytes match claimed type
# 3. Check file size
# 4. Open with PIL/Pillow — verify it's a valid image
# 5. Check dimensions
# 6. Strip EXIF metadata (may contain GPS, device info — PII)
# 7. Re-encode to PNG before OCR processing
```

### Dependency Security

- `pip-audit` runs in CI on every PR — blocks merge on known vulnerabilities
- Dependabot enabled for automated dependency update PRs
- Pin all dependencies to exact versions in `pyproject.toml` lock file
- No `*` or `>=` version specifiers in production dependencies
- Monthly manual review of dependency tree for transitive vulnerabilities

---

## Secrets Management

### By Environment

| Environment | Secret Storage | Access Control |
|-------------|---------------|----------------|
| **Local dev** | `.env` file (gitignored) | Developer's machine only |
| **CI/CD** | GitHub Actions Encrypted Secrets | Scoped per environment (staging/prod), masked in logs |
| **Staging** | AWS Secrets Manager (or GCP Secret Manager) | IAM role-based access, versioned, access-logged |
| **Production** | AWS Secrets Manager + KMS (or GCP Secret Manager + Cloud KMS) | IAM role-based, HSM-backed master key, auto-rotation where supported |

### Secret Categories

| Secret | Rotation | Auto-rotatable? |
|--------|----------|----------------|
| `DATABASE_URL` (password component) | 90 days | Yes (Secrets Manager + RDS) |
| `REDIS_URL` (password component) | 90 days | Yes (Secrets Manager + ElastiCache) |
| `ANTHROPIC_API_KEY` | Annually or on compromise | No — manual rotation |
| `GOOGLE_VISION_API_KEY` | Annually | No — manual |
| `PHISHTANK_API_KEY` | Annually | No — manual |
| `GOOGLE_SAFE_BROWSING_KEY` | Annually | No — manual |
| `SPAMHAUS_DQS_KEY` | Annually | No — manual |
| `JWT_SIGNING_KEY` (private key) | 180 days | Semi — generate new key pair, deploy, grace period for old key |
| `SENTRY_DSN` | Never (not sensitive — it's a client-side key) | N/A |

### Zero-Downtime Rotation

For secrets that can't be auto-rotated:
1. Generate new secret
2. Update Secrets Manager with new version
3. Deploy application with config that reads both old and new versions
4. After all instances have restarted, remove old version
5. Audit log records rotation event

---

## Incident Response

### Severity Levels

| Severity | Definition | Response time | Examples |
|----------|-----------|---------------|---------|
| **P0 — Critical** | Active data breach, complete service outage | 15 minutes | Database breach, credential leak, all APIs down |
| **P1 — High** | Partial breach, significant degradation | 1 hour | Single service compromised, PII exposure for limited users |
| **P2 — Medium** | Potential vulnerability, minor degradation | 4 hours | Dependency CVE (exploitable), rate limiting bypass |
| **P3 — Low** | Minor issue, no immediate risk | 24 hours | Dependency CVE (not exploitable), log misconfiguration |

### Response Playbook

```
1. DETECT
   ├── Automated: Sentry alerts, Prometheus alerts, log anomaly detection
   ├── External: User report, security researcher, bug bounty
   └── Internal: Team member discovers issue

2. TRIAGE (within response time target)
   ├── Confirm the incident is real (not false positive)
   ├── Assess severity level
   ├── Identify blast radius (what data/users affected?)
   └── Assign incident commander

3. CONTAIN
   ├── Isolate affected systems (rotate credentials, block IPs, disable keys)
   ├── Preserve evidence (snapshots, logs — do NOT delete)
   └── Communicate internally (Slack war room)

4. ERADICATE
   ├── Identify root cause
   ├── Patch vulnerability
   ├── Rotate all potentially compromised secrets
   └── Verify fix doesn't introduce new issues

5. RECOVER
   ├── Restore affected services
   ├── Verify data integrity
   ├── Monitor for recurrence
   └── Gradual traffic ramp-up

6. NOTIFY (if required)
   ├── GDPR: Supervisory authority within 72 hours, affected users "without undue delay"
   ├── DPDP: Data Protection Board of India, as prescribed
   ├── Users: Email notification with what happened, what data was affected, what we're doing
   └── Public: Blog post if significant (within 7 days)

7. POST-MORTEM (within 5 business days)
   ├── Blameless root cause analysis
   ├── Timeline of events
   ├── What went well, what didn't
   ├── Action items with owners and deadlines
   └── Published internally (and externally if public incident)
```

### Communication Templates

**User notification** (email):
> Subject: Security Notice from Savdhaan AI
>
> We are writing to inform you about a security incident that may have affected your account.
>
> **What happened**: [brief, honest description]
> **What data was involved**: [specific, not vague]
> **What we've done**: [actions taken]
> **What you should do**: [specific actions for the user]
>
> We sincerely apologize for this incident. If you have questions, contact security@savdhaan.ai.

---

## Security Testing

### Automated (CI/CD Pipeline)

| Tool | What it checks | When |
|------|---------------|------|
| `ruff` | Code quality, some security patterns | Every PR |
| `pip-audit` | Known vulnerabilities in Python dependencies | Every PR |
| `bandit` | Python-specific security issues (hardcoded passwords, SQL injection patterns, etc.) | Every PR |
| `trivy` | Container image vulnerabilities | Every Docker build |
| `checkov` | Infrastructure-as-code security (Terraform, Kubernetes manifests) | Every infra PR |
| `pytest` security tests | Auth bypass, injection, rate limit enforcement | Every PR |

### Manual / Periodic

| Activity | Frequency | Who |
|----------|-----------|-----|
| Dependency review | Monthly | Engineering team |
| Penetration test | Annually (or before major release) | Third-party security firm |
| Architecture security review | Before each MVP launch | Internal + external reviewer |
| Threat model update | Quarterly | Security-aware team member |
| Access control audit | Quarterly | Admin reviews all active keys, roles, permissions |

### Bug Bounty (Post-Launch)

- Platform: HackerOne or Bugcrowd (evaluate after MVP 2)
- Scope: savdhaan.ai, api.savdhaan.ai, app.savdhaan.ai
- Rewards: $50-$5,000 based on severity
- Safe harbor: Researchers won't be prosecuted for good-faith testing
- Response SLA: Acknowledge within 3 business days, triage within 7

---

## Vendor Security

### Third-Party API Risk Assessment

| Vendor | Data sent to them | Risk | Mitigation |
|--------|------------------|------|------------|
| **Anthropic (Claude)** | Message text for analysis | Medium — text content sent to LLM | Content deleted from our side after processing. Anthropic's data retention policy: not used for training. |
| **Google Cloud Vision** | Images for OCR | Medium — images sent to Google | EXIF stripped before sending. Google's DPA covers GDPR. |
| **Google Safe Browsing** | URLs extracted from messages | Low — only URLs, not full messages | URLs are not PII by themselves. |
| **PhishTank** | URLs | Low | Same as above |
| **URLhaus** | URLs | Low | Same as above |
| **Spamhaus** | Domains/IPs | Low — DNS queries only | No content sent, just domain lookups |
| **WHOIS/RDAP** | Domains | Low | Public data lookup |

**Policy**: Never send full message content to threat intel APIs. Only extracted entities (URLs, domains, IPs).

### Vendor Requirements

For any new third-party integration:
1. Review their security/privacy policy
2. Confirm GDPR DPA availability (if handling EU data)
3. Assess what data we send and whether it includes PII
4. Document in this file
5. Set up monitoring for vendor outages (graceful degradation)
