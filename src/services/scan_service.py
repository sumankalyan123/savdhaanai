from __future__ import annotations

import time
import uuid
from datetime import UTC, datetime, timedelta

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.schemas.scan import EntityData, EvidenceItem, ScamCardData, ScanResult
from src.core.config import settings
from src.core.constants import Channel, ContentType, RiskLevel, ScanCategory
from src.models.scan import Scan, ScanEntity, ThreatResult
from src.models.user import ApiKey
from src.services.action_engine import get_actions
from src.services.classifier import classify_content
from src.services.entity_extractor import extract_entities
from src.services.ocr_service import extract_text_from_image
from src.services.scam_card import create_scam_card
from src.services.threat_intel import check_all_threats, results_to_evidence
from src.utils.text_sanitizer import hash_content

logger = structlog.get_logger()

# Honest messaging constants
CHECKS_PERFORMED_TEXT = [
    "message_pattern_analysis",
    "entity_extraction (URLs, phones, emails, UPI, crypto)",
]
CHECKS_PERFORMED_URLS = [
    "url_reputation (Google Safe Browsing, PhishTank, URLhaus)",
    "domain_age_verification (WHOIS)",
]
CHECKS_NOT_AVAILABLE = [
    "sender_identity_verification",
    "transaction_confirmation",
    "voice_call_content_analysis",
]
CONFIDENCE_NOTES = {
    RiskLevel.CRITICAL: (
        "Strong scam indicators detected. However, no automated system is 100% accurate. "
        "If unsure, verify directly with the claimed sender through official channels."
    ),
    RiskLevel.HIGH: (
        "Multiple warning signs detected. Exercise extreme caution. "
        "Verify through official channels before taking any action."
    ),
    RiskLevel.MEDIUM: (
        "Some suspicious elements found. This could be a scam or legitimate"
        " but aggressive communication. "
        "Verify independently before sharing any personal"
        " or financial information."
    ),
    RiskLevel.LOW: (
        "Minor concerns noted but likely legitimate. Stay alert. "
        "No automated system is perfect — if something feels wrong, trust your instincts."
    ),
    RiskLevel.NONE: (
        "No scam indicators detected in our checks. However, no automated system is perfect. "
        "If something feels wrong, trust your instincts and verify directly."
    ),
}


class ScanService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def scan_text(
        self,
        content: str,
        content_type: ContentType,
        channel: Channel | None,
        category: ScanCategory,
        locale: str,
        api_key: ApiKey,
    ) -> ScanResult:
        """Full scan pipeline for text content."""
        start = time.perf_counter()

        # 1. Extract entities
        entities = await extract_entities(content)

        # 2. Run threat intel (parallel)
        threat_results = await check_all_threats(urls=entities.urls)
        threat_evidence = results_to_evidence(threat_results)

        # 3. Classify with LLM
        classification = await classify_content(content, entities, threat_evidence)

        # 4. Generate actions
        actions = get_actions(classification.scam_type, classification.risk_level)

        # 5. Build honest messaging
        checks_performed = list(CHECKS_PERFORMED_TEXT)
        if entities.urls:
            checks_performed.extend(CHECKS_PERFORMED_URLS)
        confidence_note = CONFIDENCE_NOTES.get(
            classification.risk_level, CONFIDENCE_NOTES[RiskLevel.NONE]
        )

        processing_time_ms = round((time.perf_counter() - start) * 1000)

        # 6. Persist scan
        scan = await self._save_scan(
            content=content,
            content_type=content_type,
            channel=channel,
            category=category,
            locale=locale,
            api_key=api_key,
            entities=entities,
            threat_results=threat_results,
            classification=classification,
            actions=actions,
            checks_performed=checks_performed,
            checks_not_available=CHECKS_NOT_AVAILABLE,
            confidence_note=confidence_note,
            processing_time_ms=processing_time_ms,
        )

        # 7. Create scam card if risky enough
        scam_card_data = None
        if classification.risk_score >= 40:
            card = await create_scam_card(
                db=self.db,
                scan=scan,
                classification=classification,
            )
            if card:
                base_url = (
                    "https://savdhaan.ai" if settings.is_production else "http://localhost:8000"
                )
                scam_card_data = ScamCardData(
                    card_id=card.short_id,
                    card_url=f"{base_url}/card/{card.short_id}",
                    image_url=card.image_url,
                )

        return ScanResult(
            scan_id=scan.id,
            risk_score=classification.risk_score,
            risk_level=classification.risk_level,
            scam_type=classification.scam_type,
            explanation=classification.explanation,
            evidence=classification.evidence,
            actions=actions,
            entities=entities,
            checks_performed=checks_performed,
            checks_not_available=CHECKS_NOT_AVAILABLE,
            confidence_note=confidence_note,
            scam_card=scam_card_data,
            processing_time_ms=processing_time_ms,
            created_at=scan.created_at,
        )

    async def scan_image(
        self,
        image_data: bytes,
        _content_type: str,
        channel: Channel | None,
        category: ScanCategory,
        locale: str,
        api_key: ApiKey,
    ) -> ScanResult:
        """Full scan pipeline for image content (OCR + text analysis)."""
        # OCR first
        extracted_text = await extract_text_from_image(image_data)

        if not extracted_text.strip():
            # Can't analyze — insufficient data
            scan = Scan(
                api_key_id=api_key.id,
                content_type="image",
                channel=channel,
                category=category,
                locale=locale,
                content_hash=hash_content(str(len(image_data))),
                risk_score=0,
                risk_level=RiskLevel.INSUFFICIENT,
                explanation=(
                    "We could not extract enough text from this image for a reliable assessment."
                ),
                checks_performed=["ocr_text_extraction"],
                checks_not_available=["image_content_insufficient"],
                confidence_note=(
                    "Insufficient data for analysis."
                    " When in doubt, verify through official channels."
                ),
                processing_time_ms=0,
            )
            self.db.add(scan)
            await self.db.commit()
            await self.db.refresh(scan)

            return ScanResult(
                scan_id=scan.id,
                risk_score=0,
                risk_level=RiskLevel.INSUFFICIENT,
                explanation=scan.explanation or "",
                checks_performed=["ocr_text_extraction"],
                checks_not_available=["image_content_insufficient"],
                confidence_note=scan.confidence_note or "",
                processing_time_ms=0,
                created_at=scan.created_at,
            )

        # Run the text pipeline on extracted text
        return await self.scan_text(
            content=extracted_text,
            content_type=ContentType.IMAGE,
            channel=channel,
            category=category,
            locale=locale,
            api_key=api_key,
        )

    async def get_scan(self, scan_id: uuid.UUID, api_key_id: uuid.UUID) -> ScanResult | None:
        """Retrieve a previous scan result."""
        result = await self.db.execute(
            select(Scan).where(Scan.id == scan_id, Scan.api_key_id == api_key_id)
        )
        scan = result.scalar_one_or_none()
        if scan is None:
            return None

        return ScanResult(
            scan_id=scan.id,
            risk_score=scan.risk_score or 0,
            risk_level=scan.risk_level or RiskLevel.NONE,
            scam_type=scan.scam_type,
            explanation=scan.explanation or "",
            evidence=[EvidenceItem(**e) for e in (scan.evidence or [])],
            actions=scan.actions or [],
            entities=EntityData(),  # Don't return entities from DB for privacy
            checks_performed=scan.checks_performed or [],
            checks_not_available=scan.checks_not_available or [],
            confidence_note=scan.confidence_note or "",
            processing_time_ms=scan.processing_time_ms or 0,
            created_at=scan.created_at,
        )

    async def _save_scan(
        self,
        content: str,
        content_type: ContentType,
        channel: Channel | None,
        category: ScanCategory,
        locale: str,
        api_key: ApiKey,
        entities: EntityData,
        threat_results: list,
        classification,  # noqa: ANN001
        actions: list[str],
        checks_performed: list[str],
        checks_not_available: list[str],
        confidence_note: str,
        processing_time_ms: int,
    ) -> Scan:
        """Persist scan result to database."""
        scan = Scan(
            api_key_id=api_key.id,
            content_type=content_type,
            channel=channel,
            category=category,
            locale=locale,
            raw_content=content,
            content_hash=hash_content(content),
            risk_score=classification.risk_score,
            risk_level=classification.risk_level,
            scam_type=classification.scam_type,
            explanation=classification.explanation,
            evidence=[e.model_dump() for e in classification.evidence],
            actions=actions,
            checks_performed=checks_performed,
            checks_not_available=checks_not_available,
            confidence_note=confidence_note,
            processing_time_ms=processing_time_ms,
            model_used=classification.model_used,
            content_expires_at=datetime.now(tz=UTC)
            + timedelta(hours=settings.RAW_CONTENT_RETENTION_HOURS),
        )
        self.db.add(scan)
        await self.db.flush()  # Populate scan.id before creating related entities

        # Save entities
        for url in entities.urls:
            self.db.add(ScanEntity(scan_id=scan.id, entity_type="url", value=url))
        for phone in entities.phones:
            self.db.add(ScanEntity(scan_id=scan.id, entity_type="phone", value=phone))
        for email in entities.emails:
            self.db.add(ScanEntity(scan_id=scan.id, entity_type="email", value=email))
        for upi in entities.upi_ids:
            self.db.add(ScanEntity(scan_id=scan.id, entity_type="upi", value=upi))
        for crypto in entities.crypto_addresses:
            self.db.add(ScanEntity(scan_id=scan.id, entity_type="crypto", value=crypto))

        # Save threat results
        for tr in threat_results:
            self.db.add(
                ThreatResult(
                    scan_id=scan.id,
                    source=tr.source,
                    is_threat=tr.is_threat,
                    threat_type=tr.threat_type,
                    confidence=tr.confidence,
                    details=tr.details,
                    response_time_ms=tr.response_time_ms,
                )
            )

        await self.db.commit()
        await self.db.refresh(scan)
        return scan
