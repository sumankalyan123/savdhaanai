from __future__ import annotations

from src.core.security import generate_api_key, get_key_prefix, hash_api_key, verify_api_key


def test_generate_api_key_format():
    key = generate_api_key()
    assert key.startswith("svd_")
    assert len(key) == 4 + 32  # prefix + random part


def test_generate_api_key_unique():
    keys = {generate_api_key() for _ in range(100)}
    assert len(keys) == 100  # all unique


def test_hash_and_verify():
    key = generate_api_key()
    hashed = hash_api_key(key)
    assert verify_api_key(key, hashed) is True
    assert verify_api_key("wrong_key", hashed) is False


def test_get_key_prefix():
    key = "svd_abc123def456xyz"
    assert get_key_prefix(key) == "svd_abc123de"
    assert len(get_key_prefix(key)) == 12
