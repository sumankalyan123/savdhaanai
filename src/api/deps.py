from __future__ import annotations

import uuid

from fastapi import Depends, Header, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.core.exceptions import UnauthorizedError
from src.core.security import verify_api_key
from src.models.user import ApiKey


async def get_api_key(
    x_api_key: str = Header(..., alias="X-API-Key"),
    db: AsyncSession = Depends(get_db),
) -> ApiKey:
    """Validate the API key from the request header."""
    if not x_api_key or len(x_api_key) < 12:
        raise UnauthorizedError()

    prefix = x_api_key[:12]
    result = await db.execute(
        select(ApiKey).where(ApiKey.key_prefix == prefix, ApiKey.is_active.is_(True))
    )
    api_key = result.scalar_one_or_none()

    if api_key is None:
        raise UnauthorizedError()

    if not verify_api_key(x_api_key, api_key.key_hash):
        raise UnauthorizedError()

    if api_key.revoked_at is not None:
        raise UnauthorizedError("API key has been revoked")

    return api_key


def get_request_id(request: Request) -> uuid.UUID:
    """Get the request ID from the request state."""
    return getattr(request.state, "request_id", uuid.uuid4())
