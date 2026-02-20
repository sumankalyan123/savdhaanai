# Savdhaan AI — Deployment, Hosting & Infrastructure

> Last updated: 2026-02-20

---

## Hosting Strategy

### Cloud Provider: AWS (Primary)

**Why AWS over alternatives:**

| Factor | AWS | GCP | Azure |
|--------|-----|-----|-------|
| India region | Mumbai (ap-south-1) ✓ | Mumbai ✓ | Pune ✓ |
| US region | us-east-1, us-west-2 ✓ | us-central1 ✓ | East US ✓ |
| Managed PostgreSQL | RDS — mature, reliable | Cloud SQL — good | Flexible Server — decent |
| Managed Redis | ElastiCache — battle-tested | Memorystore — good | Cache for Redis — decent |
| Kubernetes | EKS — industry standard | GKE — arguably better UX | AKS — good |
| Free tier | 12 months generous | Always-free tier | 12 months |
| Cost at scale | Moderate | Lower compute cost | Moderate |
| Ecosystem | Largest | Growing | Enterprise-heavy |

**Decision**: AWS for primary hosting. GCP for Google Cloud Vision API (OCR) only.
Can migrate to GCP later if cost savings justify it — all services are containerized and cloud-agnostic.

**Secondary consideration**: If budget-constrained at start, **Railway** or **Fly.io** for quick deploy,
migrate to AWS when scaling requires it.

---

## Environment Architecture

### Three Environments

```
┌─────────────────────────────────────────────────────────────────┐
│                        PRODUCTION                                │
│  Region: ap-south-1 (Mumbai) — primary                          │
│  Region: us-east-1 (N. Virginia) — secondary (future)           │
│                                                                  │
│  EKS Cluster                                                     │
│  ├── FastAPI pods (2-8, HPA)                                    │
│  ├── Celery worker pods (1-4, HPA)                              │
│  ├── Celery beat pod (1)                                        │
│  └── Nginx ingress controller                                   │
│                                                                  │
│  RDS PostgreSQL 16 (db.r6g.large, Multi-AZ)                    │
│  ElastiCache Redis 7 (cache.r6g.large, cluster mode)           │
│  S3 (scam card images, uploads)                                 │
│  CloudFront CDN (global edge for card pages + images)           │
│  ALB (Application Load Balancer)                                │
│  Route 53 (DNS)                                                 │
│  ACM (TLS certificates)                                         │
│  Secrets Manager + KMS                                          │
│  CloudWatch (logs + metrics)                                    │
│  ECR (container registry)                                       │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                        STAGING                                   │
│  Region: ap-south-1 (Mumbai)                                    │
│                                                                  │
│  EKS Cluster (smaller node group)                               │
│  ├── FastAPI pods (1-2)                                         │
│  ├── Celery worker pods (1)                                     │
│  └── Celery beat pod (1)                                        │
│                                                                  │
│  RDS PostgreSQL 16 (db.t4g.medium, single-AZ)                  │
│  ElastiCache Redis 7 (cache.t4g.micro)                          │
│  S3 (separate bucket)                                           │
│  ALB                                                            │
│  Secrets Manager (separate secrets)                              │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                     LOCAL DEVELOPMENT                            │
│                                                                  │
│  Docker Compose                                                  │
│  ├── FastAPI (uvicorn, hot reload)                              │
│  ├── PostgreSQL 16                                              │
│  ├── Redis 7                                                    │
│  ├── Celery worker                                              │
│  ├── Celery beat                                                │
│  ├── MinIO (S3-compatible)                                      │
│  └── MailHog (email testing, future)                            │
│                                                                  │
│  All on developer's machine via `make dev`                      │
└─────────────────────────────────────────────────────────────────┘
```

### Environment Isolation

| Concern | How it's isolated |
|---------|------------------|
| **Network** | Separate VPCs per environment. No cross-environment access. |
| **Databases** | Separate RDS instances. No shared data. |
| **Secrets** | Separate Secrets Manager secrets. Different API keys per environment. |
| **DNS** | `api.savdhaan.ai` (prod), `staging-api.savdhaan.ai` (staging), `localhost:8000` (dev) |
| **Container images** | Same image, different config via env vars. Image tagged with git SHA. |
| **IAM roles** | Separate AWS IAM roles per environment. Staging can't access prod resources. |

---

## Docker Configuration

### Dockerfile (Multi-stage)

```dockerfile
# Build stage
FROM python:3.12-slim AS builder
WORKDIR /app
COPY pyproject.toml ./
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir .

# Production stage
FROM python:3.12-slim AS production
WORKDIR /app

# Security: non-root user
RUN groupadd -r savdhaan && useradd -r -g savdhaan savdhaan

# Install Tesseract (OCR fallback)
RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr tesseract-ocr-hin tesseract-ocr-tam tesseract-ocr-tel \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY src/ ./src/
COPY alembic/ ./alembic/
COPY alembic.ini ./

USER savdhaan
EXPOSE 8000

CMD ["gunicorn", "src.api:app", \
     "--worker-class", "uvicorn.workers.UvicornWorker", \
     "--workers", "4", \
     "--bind", "0.0.0.0:8000", \
     "--timeout", "120", \
     "--access-logfile", "-"]
```

### Docker Compose (Local Dev)

```yaml
services:
  api:
    build: .
    command: uvicorn src.api:app --host 0.0.0.0 --port 8000 --reload
    ports: ["8000:8000"]
    env_file: .env
    volumes: ["./src:/app/src"]  # hot reload
    depends_on: [db, redis]

  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: savdhaan
      POSTGRES_USER: savdhaan
      POSTGRES_PASSWORD: localdev
    ports: ["5432:5432"]
    volumes: ["pgdata:/var/lib/postgresql/data"]

  redis:
    image: redis:7-alpine
    ports: ["6379:6379"]

  celery-worker:
    build: .
    command: celery -A src.workers worker --loglevel=info --concurrency=2
    env_file: .env
    depends_on: [db, redis]

  celery-beat:
    build: .
    command: celery -A src.workers beat --loglevel=info
    env_file: .env
    depends_on: [redis]

  minio:
    image: minio/minio
    command: server /data --console-address ":9001"
    ports: ["9000:9000", "9001:9001"]
    environment:
      MINIO_ROOT_USER: minioadmin
      MINIO_ROOT_PASSWORD: minioadmin

volumes:
  pgdata:
```

---

## Kubernetes (Production)

### Cluster Architecture

```
EKS Cluster (ap-south-1)
│
├── Namespace: savdhaan-prod
│   ├── Deployment: api (2-8 replicas, HPA)
│   │   └── Container: savdhaan-api
│   │       ├── Resources: 512Mi-1Gi RAM, 250m-500m CPU
│   │       ├── Health: /health (liveness + readiness)
│   │       └── Env: from Kubernetes Secrets + ConfigMap
│   │
│   ├── Deployment: celery-worker (1-4 replicas, HPA)
│   │   └── Container: savdhaan-worker
│   │       ├── Resources: 512Mi-1Gi RAM, 250m-500m CPU
│   │       └── Concurrency: 4 per pod
│   │
│   ├── Deployment: celery-beat (1 replica, no HPA)
│   │   └── Container: savdhaan-beat
│   │
│   ├── Service: api-service (ClusterIP)
│   ├── Ingress: nginx-ingress → ALB
│   ├── HPA: api-hpa (target: 70% CPU, 80% memory)
│   ├── HPA: worker-hpa (target: queue depth)
│   ├── ConfigMap: savdhaan-config
│   ├── Secret: savdhaan-secrets (from Secrets Manager via External Secrets Operator)
│   └── PodDisruptionBudget: min 1 api pod available during updates
│
├── Namespace: monitoring
│   ├── Prometheus (metrics collection)
│   ├── Grafana (dashboards)
│   └── AlertManager (notifications)
│
└── Namespace: ingress
    └── nginx-ingress-controller
```

### Auto-Scaling

| Component | Metric | Min | Max | Target |
|-----------|--------|-----|-----|--------|
| API pods | CPU utilization | 2 | 8 | 70% |
| API pods | Request rate | 2 | 8 | 100 req/s per pod |
| Celery workers | Queue depth | 1 | 4 | 10 pending tasks per worker |
| EKS nodes | Pod resource pressure | 2 | 6 | 70% allocatable used |

### Rolling Deploys

```yaml
strategy:
  type: RollingUpdate
  rollingUpdate:
    maxUnavailable: 0      # Never reduce capacity during deploy
    maxSurge: 1            # Add 1 new pod before removing old
```

- New version deployed → health check passes → old version terminated
- If health check fails → automatic rollback to previous version
- Database migrations run as a Kubernetes Job before deployment
- Feature flags for gradual rollout of new features (not needed MVP 1)

---

## CI/CD Pipeline

### GitHub Actions

```
Push to branch
     │
     ▼
┌─────────────────────────────────────────────────────────┐
│  PR Pipeline (on every push to non-main branch)          │
│                                                          │
│  ┌──────────┐  ┌──────────┐  ┌────────────┐            │
│  │   Lint   │  │  Test    │  │  Security  │   parallel  │
│  │ ruff check│  │ pytest   │  │ pip-audit  │            │
│  │ ruff format│ │ coverage │  │ bandit     │            │
│  │ mypy      │  │ report   │  │ trivy      │            │
│  └──────────┘  └──────────┘  └────────────┘            │
│       │              │              │                    │
│       └──────────────┼──────────────┘                    │
│                      ▼                                   │
│              All pass? → PR can be merged                │
└─────────────────────────────────────────────────────────┘

Merge to main
     │
     ▼
┌─────────────────────────────────────────────────────────┐
│  Deploy Pipeline                                         │
│                                                          │
│  1. Run full test suite (again, for safety)              │
│  2. Build Docker image, tag with git SHA                 │
│  3. Push image to ECR                                    │
│  4. Run Alembic migrations against staging DB            │
│  5. Deploy to staging (kubectl apply)                    │
│  6. Run smoke tests against staging                      │
│  7. ── Manual approval gate ──                           │
│  8. Run Alembic migrations against prod DB               │
│  9. Deploy to production (kubectl apply)                 │
│  10. Run smoke tests against production                  │
│  11. Monitor error rates for 10 minutes                  │
│  12. Auto-rollback if error rate > 1%                    │
└─────────────────────────────────────────────────────────┘
```

### Pipeline Details

| Stage | Tool | Timeout | Failure action |
|-------|------|---------|---------------|
| Lint | ruff check, ruff format --check, mypy | 3 min | Block merge |
| Test | pytest --cov=src/services --cov-fail-under=80 | 10 min | Block merge |
| Security scan | pip-audit, bandit, trivy | 5 min | Block merge (critical/high), warn (medium/low) |
| Build | Docker build + push to ECR | 5 min | Block deploy |
| Migrate (staging) | alembic upgrade head | 2 min | Block deploy |
| Deploy staging | kubectl set image | 3 min | Block deploy |
| Smoke tests | pytest tests/smoke/ against staging | 2 min | Block prod deploy |
| **Manual approval** | GitHub environment protection rule | — | Required for prod |
| Migrate (prod) | alembic upgrade head | 2 min | Alert + manual intervention |
| Deploy prod | kubectl set image | 3 min | Auto-rollback on failure |
| Post-deploy monitor | Check error rate via Prometheus | 10 min | Auto-rollback if > 1% |

---

## Monitoring & Observability

### Metrics (Prometheus)

**Application metrics** (exposed via `/metrics`):

| Metric | Type | Labels | Alert threshold |
|--------|------|--------|----------------|
| `http_requests_total` | Counter | method, path, status | — |
| `http_request_duration_seconds` | Histogram | method, path | p95 > 3s (text scan), p95 > 5s (image scan) |
| `scan_total` | Counter | category, risk_level, scam_type | — |
| `scan_duration_seconds` | Histogram | category, content_type | p95 > 3s |
| `llm_requests_total` | Counter | model, status | error rate > 5% |
| `llm_request_duration_seconds` | Histogram | model | p95 > 2s |
| `threat_intel_requests_total` | Counter | source, result | — |
| `threat_intel_duration_seconds` | Histogram | source | p95 > 3s |
| `threat_intel_source_up` | Gauge | source | any source down > 5 min |
| `celery_tasks_total` | Counter | task_name, status | — |
| `celery_queue_depth` | Gauge | queue_name | > 50 pending |
| `rate_limit_hits_total` | Counter | tier | — |
| `abuse_score_threshold_total` | Counter | level | — |
| `db_pool_active_connections` | Gauge | — | > 80% pool size |
| `redis_connected_clients` | Gauge | — | > 80% max connections |

**Infrastructure metrics** (via CloudWatch / node-exporter):
- CPU, memory, disk, network per node and pod
- RDS: connections, replication lag, IOPS, storage
- ElastiCache: memory usage, evictions, hit rate, connections
- ALB: request count, latency, 5xx rate

### Logging

**Format**: Structured JSON, one line per log entry.

```json
{
  "timestamp": "2026-02-20T10:30:00.123Z",
  "level": "INFO",
  "logger": "src.services.scan_service",
  "message": "Scan completed",
  "request_id": "req_abc123",
  "scan_id": "550e8400-...",
  "risk_level": "critical",
  "processing_time_ms": 2340,
  "environment": "production"
}
```

**Rules**:
- NEVER log message content, phone numbers, emails, API keys (PII/secrets)
- Every log entry includes `request_id` for request tracing
- Log levels: DEBUG (dev only), INFO (normal ops), WARNING (degradation), ERROR (failure), CRITICAL (system down)

**Storage**: CloudWatch Logs → S3 (archived after 30 days) → Glacier (after 90 days, retained 1 year)

### Alerting

| Channel | What gets sent | Escalation |
|---------|---------------|------------|
| **Slack #alerts** | All warnings and errors | First responder |
| **PagerDuty** | P0 and P1 incidents | On-call engineer, auto-escalate after 15 min |
| **Email** | Daily summary, weekly report | Engineering lead |

### Dashboards (Grafana)

1. **API Overview** — Request rate, latency percentiles, error rate, active connections
2. **Scan Pipeline** — Scans/min, duration breakdown (OCR, entity extraction, threat intel, classification), success rate
3. **Threat Intel** — Per-source availability, latency, flag rate, cache hit rate
4. **Infrastructure** — CPU, memory, pods, nodes, DB connections, Redis memory
5. **Business** — Scans by category, scam types detected, cards shared, user growth
6. **Security** — Auth failures, rate limit hits, abuse scores, flagged accounts

---

## Backup & Disaster Recovery

### Backup Strategy

| Component | Method | Frequency | Retention | Recovery test |
|-----------|--------|-----------|-----------|---------------|
| PostgreSQL | RDS automated snapshots | Daily + continuous WAL | 30 days | Monthly restore test |
| PostgreSQL | Cross-region snapshot copy | Daily | 7 days in secondary region | Quarterly |
| Redis | ElastiCache snapshot | Every 6 hours | 3 days | Monthly |
| S3 (scam cards) | S3 versioning + cross-region replication | Continuous | 90 days (versions) | Quarterly |
| Kubernetes config | GitOps (all manifests in git) | Every commit | Git history | Every deploy |
| Secrets | Secrets Manager versioning | Every rotation | 10 versions | Every rotation |

### Recovery Targets

| Scenario | RTO (Recovery Time) | RPO (Recovery Point) |
|----------|--------------------|--------------------|
| **Single pod crash** | 30 seconds (K8s auto-restart) | 0 (no data loss) |
| **Database failover** | 1-2 minutes (RDS Multi-AZ) | ~0 (synchronous replication) |
| **Full AZ outage** | 5-10 minutes (pods reschedule + DB failover) | ~0 |
| **Full region outage** | 1-2 hours (restore from cross-region backup, DNS failover) | < 24 hours |
| **Data corruption** | 30 minutes (point-in-time restore from WAL) | < 5 minutes |
| **Accidental deletion** | 15 minutes (restore from snapshot) | < 24 hours |

### Disaster Recovery Runbook

```
1. ASSESS
   └── What failed? (pod, node, AZ, region, data corruption?)

2. AUTOMATED RECOVERY (no human needed)
   ├── Pod crash → K8s restarts pod (readiness probe gates traffic)
   ├── Node failure → K8s reschedules pods to healthy nodes
   └── AZ failure → Multi-AZ DB failover + pods on remaining AZs

3. MANUAL RECOVERY (human required)
   ├── Region failure:
   │   ├── Restore DB from cross-region snapshot in secondary region
   │   ├── Deploy application to secondary region EKS cluster
   │   ├── Update Route 53 DNS to point to secondary region
   │   └── Notify users of temporary degradation
   │
   ├── Data corruption:
   │   ├── Identify corruption window (audit logs + monitoring)
   │   ├── RDS point-in-time restore to just before corruption
   │   ├── Verify restored data integrity
   │   └── Swap application to restored instance
   │
   └── Complete compromise:
       ├── Rotate ALL secrets (database, Redis, API keys, JWT signing keys)
       ├── Revoke all user API keys (users must regenerate)
       ├── Restore from last known-good backup
       ├── Forensic analysis of compromise
       └── Follow Incident Response playbook (see SECURITY.md)
```

---

## Cost Estimates

### MVP 1 — Low Traffic (< 10K scans/day)

| Service | Spec | Monthly cost (USD) |
|---------|------|-------------------|
| **EKS cluster** | Control plane | $73 |
| **EC2 nodes** (2x) | t3.medium (2 vCPU, 4GB) | $60 |
| **RDS PostgreSQL** | db.t4g.medium, 50GB, Multi-AZ | $90 |
| **ElastiCache Redis** | cache.t4g.micro, single node | $13 |
| **S3** | 10GB storage + requests | $5 |
| **CloudFront** | 100GB transfer | $10 |
| **ALB** | Application Load Balancer | $25 |
| **Secrets Manager** | 10 secrets | $4 |
| **CloudWatch** | Logs + metrics | $20 |
| **ECR** | Container images | $5 |
| **Route 53** | Hosted zone + queries | $5 |
| **Anthropic Claude API** | ~10K scans × $0.003-0.015/scan | $30-150 |
| **Google Vision API** | ~2K image scans × $1.50/1K | $3 |
| | **Total** | **~$345-465/month** |

### Budget-Conscious Alternative (MVP 1 Launch)

If full AWS is too much to start, use managed platforms:

| Service | Alternative | Monthly cost (USD) |
|---------|------------|-------------------|
| **App hosting** | Railway or Fly.io | $20-40 |
| **PostgreSQL** | Neon (free tier → $19/mo) or Supabase | $0-19 |
| **Redis** | Upstash (free tier → $10/mo) | $0-10 |
| **S3** | Cloudflare R2 (free egress) | $5 |
| **CDN** | Cloudflare (free tier) | $0 |
| **Anthropic Claude API** | Same | $30-150 |
| **Google Vision API** | Same | $3 |
| | **Total** | **~$60-230/month** |

Can start here and migrate to AWS when scaling requires it.

### Growth Phase (100K scans/day)

| Service | Spec | Monthly cost (USD) |
|---------|------|-------------------|
| **EKS** | Control plane + 4x m5.large nodes | $400 |
| **RDS PostgreSQL** | db.r6g.large, 200GB, Multi-AZ, read replica | $500 |
| **ElastiCache Redis** | cache.r6g.large, cluster mode | $300 |
| **S3 + CloudFront** | 500GB storage, 1TB transfer | $100 |
| **ALB** | Higher request volume | $50 |
| **Anthropic Claude API** | ~100K scans × $0.003-0.015 | $300-1,500 |
| **Other AWS services** | Secrets Manager, CloudWatch, ECR, Route 53 | $100 |
| | **Total** | **~$1,750-2,950/month** |

---

## Frontend Hosting (MVP 2+)

| Component | Host | Why |
|-----------|------|-----|
| **Next.js web app** | Vercel | Native Next.js support, edge functions, automatic preview deploys, great DX |
| **Scam card pages** | Vercel (SSR) + CloudFront (images) | SSR for OG tags, CDN for card images |
| **Mobile app backend** | Same FastAPI API | No separate backend needed — mobile hits the same API |

**Vercel cost**: Free tier for MVP 2 development. Pro ($20/month) when traffic grows.

---

## DNS & Domain Architecture

```
savdhaan.ai                    → Vercel (web app, MVP 2+)
www.savdhaan.ai                → Redirect to savdhaan.ai
api.savdhaan.ai                → ALB → EKS (FastAPI)
staging-api.savdhaan.ai        → ALB → Staging EKS
cdn.savdhaan.ai                → CloudFront (scam card images, static assets)
card.savdhaan.ai (future)      → Vercel (dedicated scam card pages for SEO)
status.savdhaan.ai (future)    → Status page (Betteruptime or similar)
```

**DNS provider**: Route 53 (AWS) — integrates with ACM for TLS, supports health checks and failover routing.

**TLS certificates**: AWS ACM (free, auto-renewing) for all *.savdhaan.ai subdomains.

---

## Infrastructure as Code

### Current (MVP 1)

| Tool | What it manages |
|------|----------------|
| **Docker Compose** | Local development environment |
| **Kubernetes manifests** (YAML in repo) | Staging and production deployments |
| **GitHub Actions** (YAML in repo) | CI/CD pipelines |
| **Alembic** (Python in repo) | Database schema migrations |

### Future (Growth Phase)

| Tool | What it manages |
|------|----------------|
| **Terraform** | AWS infrastructure: VPC, EKS, RDS, ElastiCache, S3, IAM, Route 53, ALB |
| **Helm charts** | Kubernetes application deployment (templated manifests) |
| **ArgoCD** (optional) | GitOps-based continuous delivery |

**Principle**: Everything in git. No manual AWS console changes. Infrastructure changes go through PR review like code.
