"""Integration tests for the full scan pipeline with LLM.

Tests the complete flow: entity extraction → threat intel → classification → actions → persist.

Run with: pytest tests/integration/test_scan_pipeline_llm.py -m llm -v
"""

from __future__ import annotations

import json
import uuid
from pathlib import Path

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings
from src.core.constants import ContentType, ScanCategory
from src.core.security import generate_api_key, get_key_prefix, hash_api_key
from src.models.scan import Scan, ScanEntity
from src.models.scam_card import ScamCard
from src.models.user import ApiKey, User
from src.services.scan_service import ScanService

FIXTURES_PATH = Path(__file__).parent.parent / "fixtures" / "scam_messages.json"

skip_no_key = pytest.mark.skipif(
    not settings.ANTHROPIC_API_KEY,
    reason="ANTHROPIC_API_KEY not configured",
)


def load_fixtures() -> dict:
    return json.loads(FIXTURES_PATH.read_text())


async def create_test_user_and_key(db: AsyncSession) -> ApiKey:
    """Create a test user and API key in the test database."""
    user = User(
        id=uuid.uuid4(),
        email=f"test-{uuid.uuid4().hex[:8]}@savdhaan.ai",
        display_name="Test User",
        is_active=True,
        plan="free",
    )
    db.add(user)
    await db.flush()

    raw_key = generate_api_key()
    api_key = ApiKey(
        id=uuid.uuid4(),
        user_id=user.id,
        key_hash=hash_api_key(raw_key),
        key_prefix=get_key_prefix(raw_key),
        label="test-key",
        plan="free",
        is_active=True,
    )
    db.add(api_key)
    await db.flush()
    return api_key


@pytest.mark.llm
@skip_no_key
async def test_full_scan_phishing_message(db_session: AsyncSession):
    """Full pipeline test: phishing message should be flagged as critical."""
    fixtures = load_fixtures()
    msg = fixtures["phishing_bank_kyc"]
    api_key = await create_test_user_and_key(db_session)

    service = ScanService(db_session)
    result = await service.scan_text(
        content=msg["text"],
        content_type=ContentType.TEXT,
        channel=None,
        category=ScanCategory.SCAM_CHECK,
        locale="en",
        api_key=api_key,
    )

    # Classification
    assert result.risk_score >= msg["expected_min_score"]
    assert result.risk_level in ("critical", "high")
    assert result.scam_type == "phishing"
    assert len(result.explanation) > 50
    assert len(result.evidence) >= 1

    # Entities extracted
    assert len(result.entities.urls) >= 1

    # Actions generated
    assert len(result.actions) >= 1

    # Honest messaging
    assert len(result.checks_performed) >= 1
    assert len(result.checks_not_available) >= 1
    assert result.confidence_note

    # Processing time
    assert result.processing_time_ms > 0

    # Scam card created (score >= 40)
    assert result.scam_card is not None
    assert result.scam_card.card_id

    # Verify persisted to DB
    db_scan = await db_session.execute(select(Scan).where(Scan.id == result.scan_id))
    scan = db_scan.scalar_one()
    assert scan.risk_score == result.risk_score
    assert scan.scam_type == "phishing"

    # Verify entities persisted
    db_entities = await db_session.execute(
        select(ScanEntity).where(ScanEntity.scan_id == result.scan_id)
    )
    entities = db_entities.scalars().all()
    assert len(entities) >= 1


@pytest.mark.llm
@skip_no_key
async def test_full_scan_benign_message(db_session: AsyncSession):
    """Full pipeline test: benign message should not be flagged."""
    fixtures = load_fixtures()
    msg = fixtures["benign_personal_message"]
    api_key = await create_test_user_and_key(db_session)

    service = ScanService(db_session)
    result = await service.scan_text(
        content=msg["text"],
        content_type=ContentType.TEXT,
        channel=None,
        category=ScanCategory.SCAM_CHECK,
        locale="en",
        api_key=api_key,
    )

    assert result.risk_score <= msg["expected_max_score"]
    assert result.risk_level == "none"

    # No scam card for benign messages (score < 40)
    assert result.scam_card is None

    # Still has honest messaging
    assert result.confidence_note
    assert result.processing_time_ms > 0


@pytest.mark.llm
@skip_no_key
async def test_full_scan_lottery_scam_creates_card(db_session: AsyncSession):
    """Lottery scam should create a shareable scam card."""
    fixtures = load_fixtures()
    msg = fixtures["lottery_prize_scam"]
    api_key = await create_test_user_and_key(db_session)

    service = ScanService(db_session)
    result = await service.scan_text(
        content=msg["text"],
        content_type=ContentType.TEXT,
        channel=None,
        category=ScanCategory.SCAM_CHECK,
        locale="en",
        api_key=api_key,
    )

    assert result.risk_score >= msg["expected_min_score"]
    assert result.scam_card is not None

    # Verify card persisted in DB
    db_card = await db_session.execute(
        select(ScamCard).where(ScamCard.short_id == result.scam_card.card_id)
    )
    card = db_card.scalar_one()
    assert card.risk_level == result.risk_level
    assert card.risk_score == result.risk_score


@pytest.mark.llm
@skip_no_key
async def test_full_scan_investment_scam_extracts_crypto(db_session: AsyncSession):
    """Investment scam with crypto address should extract and persist it."""
    fixtures = load_fixtures()
    msg = fixtures["investment_scam"]
    api_key = await create_test_user_and_key(db_session)

    service = ScanService(db_session)
    result = await service.scan_text(
        content=msg["text"],
        content_type=ContentType.TEXT,
        channel=None,
        category=ScanCategory.SCAM_CHECK,
        locale="en",
        api_key=api_key,
    )

    assert result.risk_score >= msg["expected_min_score"]
    assert len(result.entities.crypto_addresses) >= 1

    # Verify crypto entity persisted
    db_entities = await db_session.execute(
        select(ScanEntity).where(
            ScanEntity.scan_id == result.scan_id, ScanEntity.entity_type == "crypto"
        )
    )
    crypto_entities = db_entities.scalars().all()
    assert len(crypto_entities) >= 1
