# Savdhaan AI — API Design

> Last updated: 2026-02-20

---

## Base URL

```
Production:  https://api.savdhaan.ai/api/v1
Staging:     https://staging-api.savdhaan.ai/api/v1
Local dev:   http://localhost:8000/api/v1
```

## Response Envelope

All responses follow a consistent envelope:

```json
// Success
{
  "ok": true,
  "data": { ... },
  "meta": {
    "request_id": "uuid",
    "processing_time_ms": 2340
  }
}

// Error
{
  "ok": false,
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "You have exceeded the scan rate limit. Try again in 360 seconds.",
    "details": { "retry_after": 360 }
  },
  "meta": {
    "request_id": "uuid"
  }
}
```

## Authentication

### API Key (MVP 1)

Pass API key in header:
```
X-API-Key: svd_abc123def456...
```

### JWT (MVP 2+)

```
Authorization: Bearer eyJhbG...
```

---

## Endpoints

### Health & Info

#### `GET /health`

Health check for load balancers and monitoring.

**Auth**: None

**Response** `200 OK`:
```json
{
  "ok": true,
  "data": {
    "status": "healthy",
    "version": "1.0.0",
    "services": {
      "database": "ok",
      "redis": "ok",
      "celery": "ok"
    }
  }
}
```

---

### Scan

#### `POST /scan`

Submit content for scam analysis.

**Auth**: API key required

**Rate limit**: 10/hour (free), 100/hour (premium)

**Request body** (`multipart/form-data` for images, `application/json` for text):

```json
{
  "content": "Congratulations! You've won $1,000,000. Click here to claim: http://bit.ly/xyz",
  "content_type": "text",
  "channel": "sms",
  "locale": "en"
}
```

For image uploads:
```
content: <file upload>
content_type: image
channel: whatsapp
locale: en
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `content` | string or file | Yes | Text content or image file |
| `content_type` | enum | Yes | `text` or `image` |
| `channel` | enum | No | `sms`, `email`, `whatsapp`, `telegram`, `instagram`, `facebook`, `twitter`, `other` |
| `locale` | string | No | ISO 639-1 language hint (default: auto-detect) |

**Response** `200 OK`:
```json
{
  "ok": true,
  "data": {
    "scan_id": "550e8400-e29b-41d4-a716-446655440000",
    "risk_score": 87,
    "risk_level": "critical",
    "scam_type": "phishing",
    "explanation": "This message exhibits classic phishing characteristics. It creates urgency with a prize claim and directs you to a shortened URL that redirects to a domain registered only 2 days ago. The destination URL is flagged in PhishTank's phishing database.",
    "evidence": [
      {
        "type": "url_flagged",
        "source": "phishtank",
        "indicator": "http://bit.ly/xyz",
        "detail": "Resolved URL matches known phishing page (PhishTank ID: 8234567)"
      },
      {
        "type": "domain_age",
        "source": "whois",
        "indicator": "claim-prize-now.com",
        "detail": "Domain registered 2 days ago via anonymous registrar"
      },
      {
        "type": "pattern_match",
        "source": "llm_analysis",
        "indicator": "prize_claim_urgency",
        "detail": "Message uses urgency tactics and unsolicited prize claim — classic advance fee scam pattern"
      }
    ],
    "actions": [
      {
        "action": "do_not_click",
        "priority": "critical",
        "description": "Do not click the link. It leads to a known phishing page designed to steal your personal information."
      },
      {
        "action": "block_sender",
        "priority": "high",
        "description": "Block this phone number to prevent future scam messages."
      },
      {
        "action": "report_spam",
        "priority": "medium",
        "description": "Report this number as spam to your carrier by forwarding the message to 7726 (SPAM)."
      }
    ],
    "entities": {
      "urls": ["http://bit.ly/xyz"],
      "phones": [],
      "emails": [],
      "crypto_addresses": [],
      "upi_ids": []
    },
    "checks_performed": [
      "url_reputation (5 sources)",
      "domain_age_verification",
      "message_pattern_analysis"
    ],
    "checks_not_available": [
      "sender_identity_verification",
      "transaction_confirmation"
    ],
    "confidence_note": "Strong scam indicators detected. However, no automated system is 100% accurate. If unsure, verify directly with the claimed sender through official channels.",
    "scam_card": {
      "card_id": "abc123",
      "card_url": "https://savdhaan.ai/card/abc123",
      "image_url": "https://cdn.savdhaan.ai/cards/abc123.png"
    },
    "processing_time_ms": 2340
  },
  "meta": {
    "request_id": "req_xyz789"
  }
}
```

**Response fields — abuse-aware degradation:**

The `evidence` array detail level varies based on the caller's abuse score (invisible to user):

| Abuse Level | `evidence` content | `checks_performed` | `confidence_note` |
|-------------|-------------------|--------------------|--------------------|
| Normal (0-30) | Full detail: source names, IDs, specific indicators | Full list | Standard qualified note |
| Elevated (31-60) | Simplified: evidence types but no source attribution | Full list | Standard qualified note |
| High (61-80) | Verdict only: risk score + scam type + explanation | Omitted | Standard qualified note |
| Critical (81+) | Verdict only + hard throttle (1 scan/hour) | Omitted | Standard qualified note |

The user always gets the verdict and honest confidence note. Only diagnostic detail is reduced.

**Error responses:**

| Status | Code | When |
|--------|------|------|
| 400 | `INVALID_INPUT` | Missing/invalid fields |
| 401 | `UNAUTHORIZED` | Missing or invalid API key |
| 413 | `PAYLOAD_TOO_LARGE` | Image exceeds 10MB |
| 415 | `UNSUPPORTED_MEDIA_TYPE` | Image format not supported |
| 429 | `RATE_LIMIT_EXCEEDED` | Too many scans |
| 500 | `INTERNAL_ERROR` | Unexpected server error |
| 503 | `SERVICE_DEGRADED` | Partial results (some threat intel sources unavailable) |

---

#### `GET /scan/{scan_id}`

Retrieve a previous scan result.

**Auth**: API key required (must own the scan)

**Response** `200 OK`: Same structure as `POST /scan` response.

---

### Scam Cards

#### `GET /card/{card_id}`

Get scam card data (JSON).

**Auth**: None (public)

**Response** `200 OK`:
```json
{
  "ok": true,
  "data": {
    "card_id": "abc123",
    "scam_type": "phishing",
    "risk_level": "critical",
    "risk_score": 87,
    "summary": "Phishing link detected — fake prize claim redirecting to credential harvesting site.",
    "evidence_summary": [
      "URL flagged by PhishTank",
      "Domain registered 2 days ago",
      "Urgency tactics detected"
    ],
    "actions_summary": [
      "Do not click the link",
      "Block the sender",
      "Report as spam"
    ],
    "channel": "sms",
    "created_at": "2026-02-20T10:30:00Z",
    "card_url": "https://savdhaan.ai/card/abc123",
    "image_url": "https://cdn.savdhaan.ai/cards/abc123.png"
  }
}
```

#### `GET /card/{card_id}/image`

Get scam card as a PNG image (for sharing).

**Auth**: None (public)

**Response**: `200 OK` with `Content-Type: image/png`

---

### Reports / Feedback

#### `POST /report`

Submit feedback on a scan result.

**Auth**: API key required

**Request body:**
```json
{
  "scan_id": "550e8400-e29b-41d4-a716-446655440000",
  "feedback_type": "confirm_scam",
  "comment": "I checked and the link definitely goes to a fake bank site"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `scan_id` | uuid | Yes | The scan to provide feedback on |
| `feedback_type` | enum | Yes | `confirm_scam`, `false_positive`, `not_sure`, `additional_info` |
| `comment` | string | No | Optional user comment (max 500 chars) |

**Response** `201 Created`:
```json
{
  "ok": true,
  "data": {
    "report_id": "uuid",
    "status": "received",
    "message": "Thank you for your feedback. This helps improve our detection."
  }
}
```

---

### Rate Limit Info

#### `GET /rate-limit`

Check current rate limit status.

**Auth**: API key required

**Response** `200 OK`:
```json
{
  "ok": true,
  "data": {
    "tier": "free",
    "limit": 10,
    "remaining": 7,
    "reset_at": "2026-02-20T11:00:00Z",
    "window_seconds": 3600
  }
}
```

---

## Rate Limiting

| Tier | Scans/Hour | Burst | Concurrent |
|------|-----------|-------|------------|
| Free | 10 | 3 | 2 |
| Premium | 100 | 20 | 10 |
| Enterprise | 1000 | 100 | 50 |

Implemented via Redis token-bucket algorithm. Rate limit headers included in all responses:

```
X-RateLimit-Limit: 10
X-RateLimit-Remaining: 7
X-RateLimit-Reset: 1708423200
```

---

## Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `INVALID_INPUT` | 400 | Request validation failed |
| `UNAUTHORIZED` | 401 | Missing or invalid API key |
| `FORBIDDEN` | 403 | API key valid but lacks permission |
| `NOT_FOUND` | 404 | Resource not found |
| `PAYLOAD_TOO_LARGE` | 413 | Upload exceeds size limit (10MB) |
| `UNSUPPORTED_MEDIA_TYPE` | 415 | File type not supported |
| `RATE_LIMIT_EXCEEDED` | 429 | Rate limit hit |
| `INTERNAL_ERROR` | 500 | Unexpected server error |
| `SERVICE_DEGRADED` | 503 | Partial functionality available |

---

## Pagination (future endpoints)

For list endpoints (MVP 2+):
```
GET /scans?cursor=abc123&limit=20
```

Response includes:
```json
{
  "ok": true,
  "data": [...],
  "meta": {
    "cursor": "next_cursor_value",
    "has_more": true
  }
}
```

---

## Webhooks (future)

For enterprise integrations:
```json
POST <customer_webhook_url>
{
  "event": "scan.completed",
  "data": { ... scan result ... },
  "timestamp": "2026-02-20T10:30:00Z"
}
```

Signed with HMAC-SHA256 for verification.
