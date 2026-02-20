from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class CardResponse(BaseModel):
    card_id: str
    title: str
    summary: str
    risk_level: str
    risk_score: int
    scam_type: str | None = None
    card_url: str
    image_url: str | None = None
    share_count: int = 0
    view_count: int = 0
    created_at: datetime
