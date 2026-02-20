from __future__ import annotations

from src.core.constants import RiskLevel, ScamType
from src.services.action_engine import get_actions


def test_phishing_critical_actions():
    actions = get_actions(ScamType.PHISHING, RiskLevel.CRITICAL)
    assert len(actions) > 0
    assert any("click" in a.lower() for a in actions)
    assert any("block" in a.lower() for a in actions)


def test_upi_fraud_actions():
    actions = get_actions(ScamType.UPI_FRAUD, RiskLevel.HIGH)
    assert any("pin" in a.lower() for a in actions)
    assert any("collect" in a.lower() for a in actions)


def test_no_risk_actions():
    actions = get_actions(ScamType.UNKNOWN, RiskLevel.NONE)
    assert any("no scam indicators" in a.lower() for a in actions)
    assert any("no automated system" in a.lower() for a in actions)


def test_job_scam_actions():
    actions = get_actions(ScamType.JOB_SCAM, RiskLevel.HIGH)
    assert any("money" in a.lower() for a in actions)
    assert any("verify" in a.lower() for a in actions)


def test_actions_are_deduplicated():
    actions = get_actions(ScamType.PHISHING, RiskLevel.CRITICAL)
    assert len(actions) == len(set(actions))
