from __future__ import annotations

import secrets
import string

import bcrypt

from src.core.constants import API_KEY_LENGTH, API_KEY_PREFIX


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
