from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.schemas.card import CardResponse
from src.api.schemas.common import ApiResponse
from src.core.config import settings
from src.core.database import get_db
from src.core.exceptions import NotFoundError
from src.models.scam_card import ScamCard

router = APIRouter()


@router.get("/card/{short_id}", response_model=ApiResponse)
async def get_card(
    short_id: str,
    db: AsyncSession = Depends(get_db),
) -> ApiResponse:
    """Get public scam card data (no auth required)."""
    result = await db.execute(select(ScamCard).where(ScamCard.short_id == short_id))
    card = result.scalar_one_or_none()

    if card is None:
        raise NotFoundError("Card", short_id)

    # Increment view count
    await db.execute(
        update(ScamCard).where(ScamCard.id == card.id).values(view_count=ScamCard.view_count + 1)
    )
    await db.commit()

    base_url = "https://savdhaan.ai" if settings.is_production else "http://localhost:8000"

    return ApiResponse(
        ok=True,
        data=CardResponse(
            card_id=card.short_id,
            title=card.title,
            summary=card.summary,
            risk_level=card.risk_level,
            risk_score=card.risk_score,
            scam_type=card.scam_type,
            card_url=f"{base_url}/card/{card.short_id}",
            image_url=card.image_url,
            share_count=card.share_count,
            view_count=card.view_count + 1,
            created_at=card.created_at,
        ),
    )
