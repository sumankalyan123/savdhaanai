"""Tests to verify honest messaging rules are followed.

The classifier must NEVER use absolute language like 'safe', 'definitely',
'guaranteed', or '100%' in its explanations.

Run with: pytest tests/integration/test_honest_messaging.py -m llm -v
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.api.schemas.scan import EntityData
from src.core.config import settings
from src.services.classifier import classify_content

FIXTURES_PATH = Path(__file__).parent.parent / "fixtures" / "scam_messages.json"

BANNED_PHRASES = [
    "this is safe",
    "completely safe",
    "definitely a scam",
    "definitely not a scam",
    "guaranteed",
    "100% sure",
    "100% certain",
    "we are certain",
    "we are sure",
    "absolutely a scam",
    "absolutely safe",
    "certainly a scam",
    "certainly safe",
]

skip_no_key = pytest.mark.skipif(
    not settings.ANTHROPIC_API_KEY,
    reason="ANTHROPIC_API_KEY not configured",
)


def load_fixtures() -> dict:
    return json.loads(FIXTURES_PATH.read_text())


def make_entities(raw: dict) -> EntityData:
    return EntityData(
        urls=raw.get("urls", []),
        phones=raw.get("phones", []),
        emails=raw.get("emails", []),
        upi_ids=raw.get("upi_ids", []),
        crypto_addresses=raw.get("crypto_addresses", []),
    )


@pytest.mark.llm
@skip_no_key
async def test_high_risk_explanation_avoids_absolute_language():
    """Critical-risk explanations should not use absolute language."""
    fixtures = load_fixtures()
    msg = fixtures["phishing_bank_kyc"]
    result = await classify_content(msg["text"], make_entities(msg["entities"]), [])

    explanation_lower = result.explanation.lower()
    for phrase in BANNED_PHRASES:
        assert phrase not in explanation_lower, (
            f"Explanation contains banned phrase '{phrase}': {result.explanation[:200]}"
        )


@pytest.mark.llm
@skip_no_key
async def test_low_risk_explanation_avoids_absolute_language():
    """Low-risk explanations should not say 'this is safe'."""
    fixtures = load_fixtures()
    msg = fixtures["benign_personal_message"]
    result = await classify_content(msg["text"], make_entities(msg["entities"]), [])

    explanation_lower = result.explanation.lower()
    for phrase in BANNED_PHRASES:
        assert phrase not in explanation_lower, (
            f"Explanation contains banned phrase '{phrase}': {result.explanation[:200]}"
        )


@pytest.mark.llm
@skip_no_key
async def test_explanation_mentions_imperfect_system():
    """Low-risk messages should acknowledge system limitations."""
    fixtures = load_fixtures()
    msg = fixtures["benign_personal_message"]
    result = await classify_content(msg["text"], make_entities(msg["entities"]), [])

    explanation_lower = result.explanation.lower()
    assert any(
        hint in explanation_lower
        for hint in ["no automated system", "no system is perfect", "not perfect", "verify"]
    ), f"Low-risk explanation doesn't acknowledge system limitations: {result.explanation[:200]}"


@pytest.mark.llm
@skip_no_key
async def test_all_scam_messages_have_evidence():
    """Every scam classification must cite specific evidence."""
    fixtures = load_fixtures()
    scam_keys = [
        "phishing_bank_kyc",
        "upi_collect_fraud",
        "lottery_prize_scam",
        "job_scam_upfront_fee",
        "investment_scam",
        "otp_fraud",
    ]
    for key in scam_keys:
        msg = fixtures[key]
        result = await classify_content(msg["text"], make_entities(msg["entities"]), [])

        assert len(result.evidence) >= 1, (
            f"Scam '{key}' classified with no evidence"
        )
        assert len(result.explanation) >= 50, (
            f"Scam '{key}' explanation too short ({len(result.explanation)} chars)"
        )
