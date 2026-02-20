from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import JSON as JSONB
from sqlalchemy import Boolean, DateTime, Float, Integer, SmallInteger, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base import Base, UUIDPrimaryKeyMixin


class AbuseEvent(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "abuse_events"

    api_key_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)
    scan_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))
    event_type: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
    details: Mapped[dict | None] = mapped_column(JSONB, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


class AbuseScore(Base):
    __tablename__ = "abuse_scores"

    api_key_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    score: Mapped[int] = mapped_column(SmallInteger, default=0, nullable=False)
    scan_count_1h: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    flagged_ratio: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    similarity_ratio: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    entity_reuse_ratio: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    response_level: Mapped[str] = mapped_column(String(10), default="full", nullable=False)
    is_flagged: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    flagged_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )


class SemanticFingerprint(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "semantic_fingerprints"

    fingerprint: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    scan_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    api_key_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)
    scam_type: Mapped[str | None] = mapped_column(String(30))
    risk_level: Mapped[str | None] = mapped_column(String(10))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


class AuditLog(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "audit_logs"

    event_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    actor_type: Mapped[str] = mapped_column(String(20), nullable=False)
    actor_id: Mapped[str | None] = mapped_column(String(100))
    target_type: Mapped[str | None] = mapped_column(String(30))
    target_id: Mapped[str | None] = mapped_column(String(100))
    action: Mapped[str] = mapped_column(String(50), nullable=False)
    details: Mapped[dict | None] = mapped_column(JSONB, default=dict)
    ip_address: Mapped[str | None] = mapped_column(String(45))
    user_agent: Mapped[str | None] = mapped_column(String(500))
    request_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


class ScamTypeRef(Base):
    __tablename__ = "scam_types"

    code: Mapped[str] = mapped_column(String(30), primary_key=True)
    label: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(String(500))
    category: Mapped[str] = mapped_column(String(30), nullable=False)
    severity_default: Mapped[str] = mapped_column(String(10), nullable=False)
    keywords: Mapped[dict | None] = mapped_column(JSONB, default=list)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
