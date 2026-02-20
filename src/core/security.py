from __future__ import annotations

import secrets
import string
import uuid
from datetime import UTC, datetime, timedelta

import bcrypt
import jwt

from src.core.constants import API_KEY_LENGTH, API_KEY_PREFIX

# --- API Keys ---


def generate_api_key() -> str:
    """Generate a new API key with the svd_ prefix."""
    chars = string.ascii_letters + string.digits
    random_part = "".join(secrets.choice(chars) for _ in range(API_KEY_LENGTH))
    return f"{API_KEY_PREFIX}{random_part}"


def hash_api_key(api_key: str) -> str:
    """Hash an API key using bcrypt."""
    return bcrypt.hashpw(api_key.encode(), bcrypt.gensalt()).decode()


def verify_api_key(api_key: str, hashed: str) -> bool:
    """Verify an API key against its bcrypt hash."""
    return bcrypt.checkpw(api_key.encode(), hashed.encode())


def get_key_prefix(api_key: str) -> str:
    """Extract the first 12 characters of an API key for identification."""
    return api_key[:12]


# --- Passwords ---


def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, hashed: str) -> bool:
    """Verify a password against its bcrypt hash."""
    return bcrypt.checkpw(password.encode(), hashed.encode())


# --- JWT ---


def create_access_token(
    user_id: uuid.UUID,
    secret_key: str,
    algorithm: str = "HS256",
    expires_minutes: int = 60,
) -> str:
    """Create a JWT access token."""
    payload = {
        "sub": str(user_id),
        "type": "access",
        "iat": datetime.now(tz=UTC),
        "exp": datetime.now(tz=UTC) + timedelta(minutes=expires_minutes),
    }
    return jwt.encode(payload, secret_key, algorithm=algorithm)


def create_refresh_token(
    user_id: uuid.UUID,
    secret_key: str,
    algorithm: str = "HS256",
    expires_days: int = 30,
) -> str:
    """Create a JWT refresh token."""
    payload = {
        "sub": str(user_id),
        "type": "refresh",
        "iat": datetime.now(tz=UTC),
        "exp": datetime.now(tz=UTC) + timedelta(days=expires_days),
    }
    return jwt.encode(payload, secret_key, algorithm=algorithm)


def decode_token(token: str, secret_key: str, algorithm: str = "HS256") -> dict:
    """Decode and verify a JWT token. Raises jwt.PyJWTError on failure."""
    return jwt.decode(token, secret_key, algorithms=[algorithm])
