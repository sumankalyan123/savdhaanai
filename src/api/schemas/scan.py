from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from src.core.constants import Channel, ContentType, ScanCategory


class ScanRequest(BaseModel):
    content: str = Field(..., min_length=1, max_length=10_000, description="Text content to scan")
    content_type: ContentType = ContentType.TEXT
    channel: Channel | None = None
    category: ScanCategory = ScanCategory.SCAM_CHECK
    locale: str = Field(default="en", max_length=10)


class ScanImageRequest(BaseModel):
    channel: Channel | None = None
    category: ScanCategory = ScanCategory.SCAM_CHECK
    locale: str = Field(default="en", max_length=10)


class EntityData(BaseModel):
    urls: list[str] = []
    phones: list[str] = []
    emails: list[str] = []
    crypto_addresses: list[str] = []
    upi_ids: list[str] = []


class EvidenceItem(BaseModel):
    source: str
    detail: str
    is_threat: bool = False
    confidence: float | None = None


class ScamCardData(BaseModel):
    card_id: str
    card_url: str
    image_url: str | None = None


class ScanResult(BaseModel):
    scan_id: uuid.UUID
    risk_score: int
    risk_level: str
    scam_type: str | None = None
    explanation: str
    evidence: list[EvidenceItem] = []
    actions: list[str] = []
    entities: EntityData = EntityData()
    checks_performed: list[str] = []
    checks_not_available: list[str] = []
    confidence_note: str
    scam_card: ScamCardData | None = None
    processing_time_ms: int
    created_at: datetime


class ScanBrief(BaseModel):
    scan_id: uuid.UUID
    risk_score: int
    risk_level: str
    scam_type: str | None = None
    content_type: str
    created_at: datetime
