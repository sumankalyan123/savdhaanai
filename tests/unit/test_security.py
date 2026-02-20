"""Tests for JWT, password, and API key security functions."""

from __future__ import annotations

import uuid

import jwt
import pytest

from src.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    generate_api_key,
    get_key_prefix,
    hash_api_key,
    hash_password,
    verify_api_key,
    verify_password,
)

SECRET = "test-secret-key-for-jwt-testing"  # noqa: S105


# --- API Key tests ---


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


# --- Password tests ---


def test_hash_and_verify_password():
    password = "MyStr0ngP@ssword!"  # noqa: S105
    hashed = hash_password(password)
    assert verify_password(password, hashed)
    assert not verify_password("wrong_password", hashed)


def test_hash_password_unique_salts():
    password = "same_password"  # noqa: S105
    h1 = hash_password(password)
    h2 = hash_password(password)
    assert h1 != h2  # Different salts
    assert verify_password(password, h1)
    assert verify_password(password, h2)


# --- JWT tests ---


def test_create_and_decode_access_token():
    user_id = uuid.uuid4()
    token = create_access_token(user_id, SECRET)
    payload = decode_token(token, SECRET)

    assert payload["sub"] == str(user_id)
    assert payload["type"] == "access"
    assert "exp" in payload
    assert "iat" in payload


def test_create_and_decode_refresh_token():
    user_id = uuid.uuid4()
    token = create_refresh_token(user_id, SECRET)
    payload = decode_token(token, SECRET)

    assert payload["sub"] == str(user_id)
    assert payload["type"] == "refresh"


def test_decode_token_wrong_secret():
    user_id = uuid.uuid4()
    token = create_access_token(user_id, SECRET)
    with pytest.raises(jwt.InvalidSignatureError):
        decode_token(token, "wrong-secret")


def test_decode_token_expired():
    user_id = uuid.uuid4()
    token = create_access_token(user_id, SECRET, expires_minutes=-1)
    with pytest.raises(jwt.ExpiredSignatureError):
        decode_token(token, SECRET)


def test_access_token_custom_expiry():
    user_id = uuid.uuid4()
    token = create_access_token(user_id, SECRET, expires_minutes=5)
    payload = decode_token(token, SECRET)
    assert payload["sub"] == str(user_id)


def test_refresh_token_custom_expiry():
    user_id = uuid.uuid4()
    token = create_refresh_token(user_id, SECRET, expires_days=7)
    payload = decode_token(token, SECRET)
    assert payload["sub"] == str(user_id)
