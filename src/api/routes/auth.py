from __future__ import annotations

import uuid
from urllib.parse import urlencode

import httpx
import structlog
from fastapi import APIRouter, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.schemas.auth import (
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
    TokenResponse,
)
from src.api.schemas.common import ApiResponse
from src.core.config import settings
from src.core.database import get_db
from src.core.exceptions import InvalidInputError, UnauthorizedError
from src.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from src.models.user import User

logger = structlog.get_logger()

router = APIRouter()


def _make_tokens(user_id: uuid.UUID) -> TokenResponse:
    """Create access + refresh token pair."""
    return TokenResponse(
        access_token=create_access_token(
            user_id,
            settings.JWT_SECRET_KEY,
            settings.JWT_ALGORITHM,
            settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES,
        ),
        refresh_token=create_refresh_token(
            user_id,
            settings.JWT_SECRET_KEY,
            settings.JWT_ALGORITHM,
            settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS,
        ),
        expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


# --- Email/Password ---


@router.post("/auth/register", response_model=ApiResponse)
async def register(
    request: RegisterRequest,
    db: AsyncSession = Depends(get_db),
) -> ApiResponse:
    """Register a new user with email and password."""
    existing = await db.execute(select(User).where(User.email == request.email))
    if existing.scalar_one_or_none() is not None:
        raise InvalidInputError("An account with this email already exists")

    user = User(
        id=uuid.uuid4(),
        email=request.email,
        display_name=request.display_name,
        password_hash=hash_password(request.password),
        is_active=True,
        plan="free",
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    tokens = _make_tokens(user.id)
    return ApiResponse(ok=True, data=tokens)


@router.post("/auth/login", response_model=ApiResponse)
async def login(
    request: LoginRequest,
    db: AsyncSession = Depends(get_db),
) -> ApiResponse:
    """Login with email and password."""
    result = await db.execute(select(User).where(User.email == request.email))
    user = result.scalar_one_or_none()

    if user is None or not user.password_hash:
        raise UnauthorizedError("Invalid email or password")

    if not verify_password(request.password, user.password_hash):
        raise UnauthorizedError("Invalid email or password")

    if not user.is_active:
        raise UnauthorizedError("Account is deactivated")

    tokens = _make_tokens(user.id)
    return ApiResponse(ok=True, data=tokens)


@router.post("/auth/refresh", response_model=ApiResponse)
async def refresh(
    request: RefreshRequest,
    db: AsyncSession = Depends(get_db),
) -> ApiResponse:
    """Refresh an access token using a refresh token."""
    try:
        payload = decode_token(
            request.refresh_token, settings.JWT_SECRET_KEY, settings.JWT_ALGORITHM
        )
    except Exception as e:
        raise UnauthorizedError("Invalid or expired refresh token") from e

    if payload.get("type") != "refresh":
        raise UnauthorizedError("Invalid token type")

    user_id = uuid.UUID(payload["sub"])
    result = await db.execute(select(User).where(User.id == user_id, User.is_active.is_(True)))
    user = result.scalar_one_or_none()
    if user is None:
        raise UnauthorizedError("User not found or deactivated")

    tokens = _make_tokens(user.id)
    return ApiResponse(ok=True, data=tokens)


# --- Google OAuth ---


@router.get("/auth/google")
async def google_login() -> RedirectResponse:
    """Redirect to Google OAuth consent screen."""
    if not settings.GOOGLE_CLIENT_ID:
        raise InvalidInputError("Google OAuth is not configured")

    params = urlencode(
        {
            "client_id": settings.GOOGLE_CLIENT_ID,
            "redirect_uri": settings.GOOGLE_REDIRECT_URI,
            "response_type": "code",
            "scope": "openid email profile",
            "access_type": "offline",
            "prompt": "consent",
        }
    )
    return RedirectResponse(f"https://accounts.google.com/o/oauth2/v2/auth?{params}")


@router.get("/auth/google/callback", response_model=ApiResponse)
async def google_callback(
    code: str,
    db: AsyncSession = Depends(get_db),
) -> ApiResponse:
    """Handle Google OAuth callback."""
    async with httpx.AsyncClient(timeout=10.0) as client:
        # Exchange code for tokens
        token_resp = await client.post(
            "https://oauth2.googleapis.com/token",
            data={
                "code": code,
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "redirect_uri": settings.GOOGLE_REDIRECT_URI,
                "grant_type": "authorization_code",
            },
        )
        if token_resp.status_code != 200:
            raise UnauthorizedError("Failed to exchange Google authorization code")

        token_data = token_resp.json()
        access_token = token_data["access_token"]

        # Get user info
        user_resp = await client.get(
            "https://www.googleapis.com/oauth2/v2/userinfo",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        if user_resp.status_code != 200:
            raise UnauthorizedError("Failed to fetch Google user info")

        google_user = user_resp.json()

    email = google_user.get("email")
    if not email:
        raise UnauthorizedError("Google account has no email")

    # Find or create user
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    if user is None:
        user = User(
            id=uuid.uuid4(),
            email=email,
            display_name=google_user.get("name"),
            is_active=True,
            plan="free",
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)

    tokens = _make_tokens(user.id)
    return ApiResponse(ok=True, data=tokens)


# --- GitHub OAuth ---


@router.get("/auth/github")
async def github_login() -> RedirectResponse:
    """Redirect to GitHub OAuth authorization."""
    if not settings.GITHUB_CLIENT_ID:
        raise InvalidInputError("GitHub OAuth is not configured")

    params = urlencode(
        {
            "client_id": settings.GITHUB_CLIENT_ID,
            "redirect_uri": settings.GITHUB_REDIRECT_URI,
            "scope": "user:email",
        }
    )
    return RedirectResponse(f"https://github.com/login/oauth/authorize?{params}")


@router.get("/auth/github/callback", response_model=ApiResponse)
async def github_callback(
    code: str,
    db: AsyncSession = Depends(get_db),
) -> ApiResponse:
    """Handle GitHub OAuth callback."""
    async with httpx.AsyncClient(timeout=10.0) as client:
        # Exchange code for token
        token_resp = await client.post(
            "https://github.com/login/oauth/access_token",
            json={
                "client_id": settings.GITHUB_CLIENT_ID,
                "client_secret": settings.GITHUB_CLIENT_SECRET,
                "code": code,
                "redirect_uri": settings.GITHUB_REDIRECT_URI,
            },
            headers={"Accept": "application/json"},
        )
        if token_resp.status_code != 200:
            raise UnauthorizedError("Failed to exchange GitHub authorization code")

        token_data = token_resp.json()
        access_token = token_data.get("access_token")
        if not access_token:
            raise UnauthorizedError("GitHub did not return an access token")

        # Get user info
        user_resp = await client.get(
            "https://api.github.com/user",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        github_user = user_resp.json()

        # Get primary email
        email = github_user.get("email")
        if not email:
            emails_resp = await client.get(
                "https://api.github.com/user/emails",
                headers={"Authorization": f"Bearer {access_token}"},
            )
            emails = emails_resp.json()
            primary = next((e for e in emails if e.get("primary")), None)
            email = primary["email"] if primary else None

    if not email:
        raise UnauthorizedError("GitHub account has no email")

    # Find or create user
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    if user is None:
        user = User(
            id=uuid.uuid4(),
            email=email,
            display_name=github_user.get("name") or github_user.get("login"),
            is_active=True,
            plan="free",
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)

    tokens = _make_tokens(user.id)
    return ApiResponse(ok=True, data=tokens)
