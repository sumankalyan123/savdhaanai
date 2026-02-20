from __future__ import annotations

import structlog
from redis.asyncio import Redis

from src.core.config import settings
from src.core.exceptions import RateLimitExceededError

logger = structlog.get_logger()

_redis: Redis | None = None


async def get_redis() -> Redis:
    """Get or create a Redis connection."""
    global _redis  # noqa: PLW0603
    if _redis is None:
        _redis = Redis.from_url(settings.REDIS_URL, decode_responses=True)
    return _redis


async def close_redis() -> None:
    """Close the Redis connection."""
    global _redis  # noqa: PLW0603
    if _redis is not None:
        await _redis.close()
        _redis = None


async def check_rate_limit(api_key_id: str, plan: str) -> None:
    """Check and increment the rate limit counter for an API key.

    Raises RateLimitExceededError if the limit is exceeded.
    """
    redis = await get_redis()
    limit = settings.RATE_LIMIT_PREMIUM if plan == "premium" else settings.RATE_LIMIT_FREE
    window = settings.RATE_LIMIT_WINDOW_SECONDS
    key = f"ratelimit:{api_key_id}"

    try:
        current = await redis.get(key)
        if current is not None and int(current) >= limit:
            ttl = await redis.ttl(key)
            retry_after = max(ttl, 1)
            raise RateLimitExceededError(
                message=f"Rate limit exceeded. Limit: {limit} requests per hour.",
                retry_after=retry_after,
            )

        pipe = redis.pipeline()
        pipe.incr(key)
        pipe.expire(key, window, nx=True)
        await pipe.execute()
    except RateLimitExceededError:
        raise
    except Exception as e:
        # If Redis is down, allow the request (graceful degradation)
        await logger.awarning("rate_limit_check_failed", error=str(e))
