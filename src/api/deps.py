from __future__ import annotations

import uuid

from fastapi import Depends, Header, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings
from src.core.database import get_db
from src.core.exceptions import UnauthorizedError
from src.core.security import decode_token, verify_api_key
from src.models.user import ApiKey, User


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


async def get_current_user(
    authorization: str = Header(..., alias="Authorization"),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Extract and validate the current user from a JWT Bearer token."""
    if not authorization.startswith("Bearer "):
        raise UnauthorizedError("Invalid authorization header")

    token = authorization[7:]
    try:
        payload = decode_token(token, settings.JWT_SECRET_KEY, settings.JWT_ALGORITHM)
    except Exception as e:
        raise UnauthorizedError("Invalid or expired token") from e

    if payload.get("type") != "access":
        raise UnauthorizedError("Invalid token type")

    user_id = uuid.UUID(payload["sub"])
    result = await db.execute(select(User).where(User.id == user_id, User.is_active.is_(True)))
    user = result.scalar_one_or_none()
    if user is None:
        raise UnauthorizedError("User not found or deactivated")

    return user


def get_request_id(request: Request) -> uuid.UUID:
    """Get the request ID from the request state."""
    return getattr(request.state, "request_id", uuid.uuid4())
