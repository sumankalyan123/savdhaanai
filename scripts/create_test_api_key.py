"""Create a test API key for local development."""
from __future__ import annotations

import asyncio
import uuid

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from src.core.config import settings
from src.core.security import generate_api_key, get_key_prefix, hash_api_key


async def create_test_key() -> None:
    engine = create_async_engine(settings.DATABASE_URL)
    raw_key = generate_api_key()
    key_hash = hash_api_key(raw_key)
    key_prefix = get_key_prefix(raw_key)
    user_id = uuid.uuid4()
    key_id = uuid.uuid4()

    async with engine.begin() as conn:
        # Create a test user
        await conn.execute(
            text("""
                INSERT INTO users (id, email, display_name, is_active, plan)
                VALUES (:id, :email, :name, true, 'free')
                ON CONFLICT (email) DO NOTHING
            """),
            {"id": str(user_id), "email": "test@savdhaan.ai", "name": "Test User"},
        )

        # Get user id (in case it already existed)
        result = await conn.execute(
            text("SELECT id FROM users WHERE email = 'test@savdhaan.ai'")
        )
        user_id = result.scalar_one()

        # Create API key
        await conn.execute(
            text("""
                INSERT INTO api_keys (id, user_id, key_hash, key_prefix, label, plan, is_active)
                VALUES (:id, :user_id, :key_hash, :key_prefix, :label, 'free', true)
            """),
            {
                "id": str(key_id),
                "user_id": str(user_id),
                "key_hash": key_hash,
                "key_prefix": key_prefix,
                "label": "dev-test-key",
            },
        )

    await engine.dispose()
    print(f"API Key created: {raw_key}")
    print(f"Prefix: {key_prefix}")
    print(f"Use in requests: -H 'X-API-Key: {raw_key}'")


if __name__ == "__main__":
    asyncio.run(create_test_key())
