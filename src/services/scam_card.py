from __future__ import annotations

import secrets
import string

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.scam_card import ScamCard
from src.models.scan import Scan
from src.services.classifier import ClassificationResult

logger = structlog.get_logger()


def _generate_short_id(length: int = 8) -> str:
    """Generate a URL-safe short ID for scam cards."""
    chars = string.ascii_lowercase + string.digits
    return "".join(secrets.choice(chars) for _ in range(length))


def _generate_card_title(classification: ClassificationResult) -> str:
    """Generate a descriptive title for the scam card."""
    scam_labels = {
        "phishing": "Phishing Alert",
        "smishing": "SMS Scam Alert",
        "upi_fraud": "UPI Fraud Alert",
        "advance_fee": "Advance Fee Scam Alert",
        "lottery_prize": "Lottery/Prize Scam Alert",
        "job_scam": "Job Scam Alert",
        "investment_scam": "Investment Scam Alert",
        "tech_support": "Tech Support Scam Alert",
        "impersonation": "Impersonation Alert",
        "otp_fraud": "OTP Fraud Alert",
        "crypto_scam": "Crypto Scam Alert",
        "romance_scam": "Romance Scam Alert",
        "delivery_scam": "Delivery Scam Alert",
    }
    return scam_labels.get(classification.scam_type, "Scam Alert")


def _generate_summary(classification: ClassificationResult) -> str:
    """Generate a shareable summary for the scam card."""
    level_prefix = {
        "critical": "CRITICAL WARNING",
        "high": "HIGH RISK",
        "medium": "CAUTION",
    }
    prefix = level_prefix.get(classification.risk_level, "Warning")

    # Truncate explanation for the card
    explanation = classification.explanation
    if len(explanation) > 200:
        explanation = explanation[:197] + "..."

    return f"{prefix}: {explanation}"


async def create_scam_card(
    db: AsyncSession,
    scan: Scan,
    classification: ClassificationResult,
) -> ScamCard | None:
    """Create a shareable scam card from a scan result."""
    try:
        card = ScamCard(
            scan_id=scan.id,
            short_id=_generate_short_id(),
            title=_generate_card_title(classification),
            summary=_generate_summary(classification),
            risk_level=classification.risk_level,
            risk_score=classification.risk_score,
            scam_type=classification.scam_type,
        )
        db.add(card)
        await db.commit()
        await db.refresh(card)
        return card
    except Exception:
        await logger.aexception("scam_card_creation_failed", scan_id=str(scan.id))
        await db.rollback()
        return None
