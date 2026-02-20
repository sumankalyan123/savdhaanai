"""Integration tests for the LLM classifier using real Claude API calls.

Run with: pytest tests/integration/test_classifier_llm.py -m llm -v
These tests make real API calls and cost money. They require ANTHROPIC_API_KEY in .env.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.api.schemas.scan import EntityData, EvidenceItem
from src.core.config import settings
from src.services.classifier import ClassificationResult, classify_content

FIXTURES_PATH = Path(__file__).parent.parent / "fixtures" / "scam_messages.json"

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


# --- Scam detection tests (should flag as risky) ---


@pytest.mark.llm
@skip_no_key
async def test_classify_phishing_bank_kyc():
    fixtures = load_fixtures()
    msg = fixtures["phishing_bank_kyc"]
    result = await classify_content(msg["text"], make_entities(msg["entities"]), [])

    assert isinstance(result, ClassificationResult)
    assert result.risk_score >= msg["expected_min_score"]
    assert result.risk_level in ("critical", "high")
    assert result.scam_type == "phishing"
    assert len(result.evidence) > 0
    assert result.model_used != "fallback"


@pytest.mark.llm
@skip_no_key
async def test_classify_upi_collect_fraud():
    fixtures = load_fixtures()
    msg = fixtures["upi_collect_fraud"]
    result = await classify_content(msg["text"], make_entities(msg["entities"]), [])

    assert result.risk_score >= msg["expected_min_score"]
    assert result.risk_level in ("critical", "high")
    assert result.scam_type == "upi_fraud"


@pytest.mark.llm
@skip_no_key
async def test_classify_lottery_prize_scam():
    fixtures = load_fixtures()
    msg = fixtures["lottery_prize_scam"]
    result = await classify_content(msg["text"], make_entities(msg["entities"]), [])

    assert result.risk_score >= msg["expected_min_score"]
    assert result.risk_level == "critical"
    assert result.scam_type == "lottery_prize"


@pytest.mark.llm
@skip_no_key
async def test_classify_job_scam():
    fixtures = load_fixtures()
    msg = fixtures["job_scam_upfront_fee"]
    result = await classify_content(msg["text"], make_entities(msg["entities"]), [])

    assert result.risk_score >= msg["expected_min_score"]
    assert result.risk_level in ("critical", "high")
    assert result.scam_type == "job_scam"


@pytest.mark.llm
@skip_no_key
async def test_classify_investment_scam():
    fixtures = load_fixtures()
    msg = fixtures["investment_scam"]
    result = await classify_content(msg["text"], make_entities(msg["entities"]), [])

    assert result.risk_score >= msg["expected_min_score"]
    assert result.risk_level in ("critical", "high")
    assert result.scam_type == "investment_scam"


@pytest.mark.llm
@skip_no_key
async def test_classify_tech_support_scam():
    fixtures = load_fixtures()
    msg = fixtures["tech_support_scam"]
    result = await classify_content(msg["text"], make_entities(msg["entities"]), [])

    assert result.risk_score >= msg["expected_min_score"]
    assert result.risk_level in ("critical", "high")
    assert result.scam_type == "tech_support"


@pytest.mark.llm
@skip_no_key
async def test_classify_otp_fraud():
    fixtures = load_fixtures()
    msg = fixtures["otp_fraud"]
    result = await classify_content(msg["text"], make_entities(msg["entities"]), [])

    assert result.risk_score >= msg["expected_min_score"]
    assert result.risk_level in ("critical", "high")
    assert result.scam_type == "otp_fraud"


@pytest.mark.llm
@skip_no_key
async def test_classify_delivery_scam():
    fixtures = load_fixtures()
    msg = fixtures["delivery_scam"]
    result = await classify_content(msg["text"], make_entities(msg["entities"]), [])

    assert result.risk_score >= msg["expected_min_score"]
    assert result.risk_level in ("critical", "high")
    assert result.scam_type == "delivery_scam"


# --- Legitimate message tests (should NOT flag) ---


@pytest.mark.llm
@skip_no_key
async def test_classify_legitimate_marketing():
    fixtures = load_fixtures()
    msg = fixtures["legitimate_marketing"]
    result = await classify_content(msg["text"], make_entities(msg["entities"]), [])

    assert result.risk_score <= msg["expected_max_score"]
    assert result.risk_level in ("none", "low")


@pytest.mark.llm
@skip_no_key
async def test_classify_benign_personal_message():
    fixtures = load_fixtures()
    msg = fixtures["benign_personal_message"]
    result = await classify_content(msg["text"], make_entities(msg["entities"]), [])

    assert result.risk_score <= msg["expected_max_score"]
    assert result.risk_level == "none"


@pytest.mark.llm
@skip_no_key
async def test_classify_edge_case_empty_entities():
    fixtures = load_fixtures()
    msg = fixtures["edge_case_empty_entities"]
    result = await classify_content(msg["text"], make_entities(msg["entities"]), [])

    assert result.risk_score <= msg["expected_max_score"]
    assert result.risk_level in ("none", "low")


@pytest.mark.llm
@skip_no_key
async def test_classify_edge_case_mixed_signals():
    fixtures = load_fixtures()
    msg = fixtures["edge_case_mixed_signals"]
    result = await classify_content(msg["text"], make_entities(msg["entities"]), [])

    assert result.risk_score <= msg["expected_max_score"]
    assert result.risk_level in ("none", "low")


# --- Classification quality tests ---


@pytest.mark.llm
@skip_no_key
async def test_classifier_provides_evidence():
    """Every classification must include at least one evidence item."""
    fixtures = load_fixtures()
    msg = fixtures["phishing_bank_kyc"]
    result = await classify_content(msg["text"], make_entities(msg["entities"]), [])

    assert len(result.evidence) >= 1
    for e in result.evidence:
        assert isinstance(e, EvidenceItem)
        assert e.detail  # evidence must have a detail string


@pytest.mark.llm
@skip_no_key
async def test_classifier_threat_intel_merged():
    """Threat intel evidence should be merged into classification results."""
    fixtures = load_fixtures()
    msg = fixtures["phishing_bank_kyc"]
    threat_evidence = [
        EvidenceItem(
            source="phishtank",
            detail="URL flagged as phishing by PhishTank",
            is_threat=True,
            confidence=0.95,
        )
    ]
    result = await classify_content(msg["text"], make_entities(msg["entities"]), threat_evidence)

    sources = [e.source for e in result.evidence]
    assert "phishtank" in sources  # threat intel preserved
    assert "pattern_analysis" in sources  # LLM analysis added


@pytest.mark.llm
@skip_no_key
async def test_classifier_threat_intel_boosts_score():
    """Flagged threat intel should boost the risk score."""
    fixtures = load_fixtures()
    msg = fixtures["delivery_scam"]
    threat_evidence = [
        EvidenceItem(
            source="safe_browsing",
            detail="URL flagged by Google Safe Browsing as SOCIAL_ENGINEERING",
            is_threat=True,
            confidence=1.0,
        ),
        EvidenceItem(
            source="urlhaus",
            detail="URL found in URLhaus malware database",
            is_threat=True,
            confidence=0.9,
        ),
    ]
    result = await classify_content(msg["text"], make_entities(msg["entities"]), threat_evidence)

    # With threat intel, should be critical
    assert result.risk_score >= 80
    assert result.risk_level == "critical"
