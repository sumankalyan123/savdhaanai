from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import JSON as JSONB
from sqlalchemy import DateTime, Float, Integer, SmallInteger, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class Scan(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "scans"

    api_key_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)
    content_type: Mapped[str] = mapped_column(String(10), nullable=False)  # text, image
    channel: Mapped[str | None] = mapped_column(String(20))
    category: Mapped[str] = mapped_column(String(20), default="scam_check", nullable=False)
    locale: Mapped[str] = mapped_column(String(10), default="en", nullable=False)

    # Raw content — auto-deleted after retention window
    raw_content: Mapped[str | None] = mapped_column(Text)
    content_hash: Mapped[str] = mapped_column(String(64), nullable=False, index=True)

    # OCR result (if image)
    extracted_text: Mapped[str | None] = mapped_column(Text)

    # Classification results
    risk_score: Mapped[int | None] = mapped_column(SmallInteger)
    risk_level: Mapped[str | None] = mapped_column(String(15))
    scam_type: Mapped[str | None] = mapped_column(String(30))
    explanation: Mapped[str | None] = mapped_column(Text)
    evidence: Mapped[dict | None] = mapped_column(JSONB, default=list)
    actions: Mapped[dict | None] = mapped_column(JSONB, default=list)

    # Honest messaging
    checks_performed: Mapped[dict | None] = mapped_column(JSONB, default=list)
    checks_not_available: Mapped[dict | None] = mapped_column(JSONB, default=list)
    confidence_note: Mapped[str | None] = mapped_column(Text)

    # Processing metadata
    processing_time_ms: Mapped[int | None] = mapped_column(Integer)
    model_used: Mapped[str | None] = mapped_column(String(50))

    # Content auto-deletion tracking
    content_expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    # Relationships
    entities: Mapped[list[ScanEntity]] = relationship(back_populates="scan", lazy="selectin")
    threat_results: Mapped[list[ThreatResult]] = relationship(
        back_populates="scan", lazy="selectin"
    )


class ScanEntity(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "scan_entities"

    scan_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)
    entity_type: Mapped[str] = mapped_column(String(20), nullable=False)  # url, phone, email, etc.
    value: Mapped[str] = mapped_column(String(2048), nullable=False)
    normalized_value: Mapped[str | None] = mapped_column(String(2048))
    metadata_: Mapped[dict | None] = mapped_column("metadata", JSONB, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    scan: Mapped[Scan] = relationship(back_populates="entities")


class ThreatResult(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "threat_results"

    scan_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)
    entity_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))
    source: Mapped[str] = mapped_column(
        String(30), nullable=False
    )  # phishtank, safe_browsing, etc.
    is_threat: Mapped[bool | None] = mapped_column(default=False)
    threat_type: Mapped[str | None] = mapped_column(String(50))
    confidence: Mapped[float | None] = mapped_column(Float)
    details: Mapped[dict | None] = mapped_column(JSONB, default=dict)
    raw_response: Mapped[dict | None] = mapped_column(JSONB)  # Auto-deleted after 24h
    response_time_ms: Mapped[int | None] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    scan: Mapped[Scan] = relationship(back_populates="threat_results")
