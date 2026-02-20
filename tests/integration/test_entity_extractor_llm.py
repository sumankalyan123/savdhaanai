"""Integration tests for LLM-powered entity extraction.

Run with: pytest tests/integration/test_entity_extractor_llm.py -m llm -v
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.core.config import settings
from src.services.entity_extractor import extract_entities

FIXTURES_PATH = Path(__file__).parent.parent / "fixtures" / "scam_messages.json"

skip_no_key = pytest.mark.skipif(
    not settings.ANTHROPIC_API_KEY,
    reason="ANTHROPIC_API_KEY not configured",
)


def load_fixtures() -> dict:
    return json.loads(FIXTURES_PATH.read_text())


@pytest.mark.llm
@skip_no_key
async def test_extract_urls_from_phishing():
    fixtures = load_fixtures()
    msg = fixtures["phishing_bank_kyc"]
    entities = await extract_entities(msg["text"])

    assert "http://sbi-kyc-update.xyz/verify" in entities.urls


@pytest.mark.llm
@skip_no_key
async def test_extract_upi_ids():
    fixtures = load_fixtures()
    msg = fixtures["upi_collect_fraud"]
    entities = await extract_entities(msg["text"])

    assert any("merchant@ybl" in upi for upi in entities.upi_ids)


@pytest.mark.llm
@skip_no_key
async def test_extract_emails():
    fixtures = load_fixtures()
    msg = fixtures["job_scam_upfront_fee"]
    entities = await extract_entities(msg["text"])

    assert "hr.google.jobs@gmail.com" in entities.emails


@pytest.mark.llm
@skip_no_key
async def test_extract_crypto_addresses():
    fixtures = load_fixtures()
    msg = fixtures["investment_scam"]
    entities = await extract_entities(msg["text"])

    assert any(
        "0x742d35Cc6634C0532925a3b844Bc9e7595f2bD38" in addr for addr in entities.crypto_addresses
    )


@pytest.mark.llm
@skip_no_key
async def test_extract_no_entities_from_benign_message():
    fixtures = load_fixtures()
    msg = fixtures["benign_personal_message"]
    entities = await extract_entities(msg["text"])

    assert len(entities.urls) == 0
    assert len(entities.phones) == 0
    assert len(entities.emails) == 0
    assert len(entities.upi_ids) == 0
    assert len(entities.crypto_addresses) == 0


@pytest.mark.llm
@skip_no_key
async def test_extract_legitimate_urls():
    fixtures = load_fixtures()
    msg = fixtures["edge_case_mixed_signals"]
    entities = await extract_entities(msg["text"])

    assert any("flipkart.com" in url for url in entities.urls)


@pytest.mark.llm
@skip_no_key
async def test_extract_multiple_upi_ids():
    """LLM should extract UPI IDs from lottery scam."""
    fixtures = load_fixtures()
    msg = fixtures["lottery_prize_scam"]
    entities = await extract_entities(msg["text"])

    assert any("winner@paytm" in upi for upi in entities.upi_ids)
