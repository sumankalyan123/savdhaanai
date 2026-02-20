"""Tests for Redis rate limiter (mocked Redis)."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.api.middleware.rate_limiter import check_rate_limit
from src.core.exceptions import RateLimitExceededError


def _make_redis_mock(current_count: str | None) -> MagicMock:
    """Create a mock Redis with proper sync pipeline() and async get()."""
    redis = MagicMock()
    redis.get = AsyncMock(return_value=current_count)
    redis.ttl = AsyncMock(return_value=1800)

    pipe = MagicMock()
    pipe.execute = AsyncMock()
    redis.pipeline.return_value = pipe

    return redis


@patch("src.api.middleware.rate_limiter.get_redis")
async def test_rate_limit_allows_under_limit(mock_get_redis: AsyncMock):
    redis = _make_redis_mock("5")
    mock_get_redis.return_value = redis

    await check_rate_limit("test-key-id", "free")

    redis.pipeline.assert_called_once()
    pipe = redis.pipeline.return_value
    pipe.incr.assert_called_once()
    pipe.expire.assert_called_once()
    pipe.execute.assert_called_once()


@patch("src.api.middleware.rate_limiter.get_redis")
async def test_rate_limit_blocks_over_limit(mock_get_redis: AsyncMock):
    redis = _make_redis_mock("10")
    mock_get_redis.return_value = redis

    with pytest.raises(RateLimitExceededError):
        await check_rate_limit("test-key-id", "free")


@patch("src.api.middleware.rate_limiter.get_redis")
async def test_rate_limit_premium_higher_limit(mock_get_redis: AsyncMock):
    redis = _make_redis_mock("50")
    mock_get_redis.return_value = redis

    # Should not raise (50 < 100 premium limit)
    await check_rate_limit("test-key-id", "premium")


@patch("src.api.middleware.rate_limiter.get_redis")
async def test_rate_limit_first_request(mock_get_redis: AsyncMock):
    redis = _make_redis_mock(None)
    mock_get_redis.return_value = redis

    await check_rate_limit("new-key-id", "free")
    pipe = redis.pipeline.return_value
    pipe.incr.assert_called_once()


@patch("src.api.middleware.rate_limiter.get_redis")
async def test_rate_limit_redis_down_allows_request(mock_get_redis: AsyncMock):
    redis = MagicMock()
    redis.get = AsyncMock(side_effect=ConnectionError("Redis down"))
    mock_get_redis.return_value = redis

    # Should NOT raise — graceful degradation
    await check_rate_limit("test-key-id", "free")
