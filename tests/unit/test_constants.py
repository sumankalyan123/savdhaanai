from __future__ import annotations

from src.core.constants import RISK_THRESHOLDS, RiskLevel, ScamType


def test_risk_levels_complete():
    levels = {rl.value for rl in RiskLevel}
    assert "critical" in levels
    assert "high" in levels
    assert "medium" in levels
    assert "low" in levels
    assert "none" in levels


def test_scam_types_exist():
    assert len(ScamType) >= 18


def test_risk_thresholds_cover_full_range():
    all_scores = set()
    for low, high in RISK_THRESHOLDS.values():
        all_scores.update(range(low, high + 1))
    assert 0 in all_scores
    assert 100 in all_scores
