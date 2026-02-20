from __future__ import annotations

import uuid

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.constants import ResponseLevel
from src.models.abuse import AbuseScore

logger = structlog.get_logger()


async def get_response_level(db: AsyncSession, api_key_id: uuid.UUID) -> str:
    """Get the current response level for an API key based on abuse score."""
    result = await db.execute(select(AbuseScore).where(AbuseScore.api_key_id == api_key_id))
    abuse_score = result.scalar_one_or_none()

    if abuse_score is None:
        return ResponseLevel.FULL

    return abuse_score.response_level


def filter_evidence_by_level(evidence: list[dict], response_level: str) -> list[dict]:
    """Filter evidence detail based on the abuse response level."""
    if response_level == ResponseLevel.FULL:
        return evidence

    if response_level == ResponseLevel.REDUCED:
        # Remove source attribution but keep evidence types
        return [{**e, "source": "analysis", "detail": e.get("detail", "")} for e in evidence]

    if response_level in (ResponseLevel.MINIMAL, ResponseLevel.THROTTLED):
        # Verdict only — no evidence details
        return []

    return evidence
