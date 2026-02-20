"""Tests for auth endpoints: register, login, refresh, me."""

from __future__ import annotations

from collections.abc import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient

from src.main import app


@pytest.fixture
async def auth_client() -> AsyncGenerator[AsyncClient, None]:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


async def test_register_new_user(auth_client: AsyncClient):
    resp = await auth_client.post(
        "/api/v1/auth/register",
        json={
            "email": "newuser@example.com",
            "password": "StrongP@ss1",
            "display_name": "New User",
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["ok"] is True
    assert "access_token" in data["data"]
    assert "refresh_token" in data["data"]
    assert data["data"]["token_type"] == "bearer"  # noqa: S105
    assert data["data"]["expires_in"] > 0


async def test_register_duplicate_email(auth_client: AsyncClient):
    # Register first
    await auth_client.post(
        "/api/v1/auth/register",
        json={"email": "dup@example.com", "password": "StrongP@ss1"},
    )
    # Try again with same email
    resp = await auth_client.post(
        "/api/v1/auth/register",
        json={"email": "dup@example.com", "password": "StrongP@ss2"},
    )
    assert resp.status_code == 400
    assert resp.json()["ok"] is False


async def test_register_short_password(auth_client: AsyncClient):
    resp = await auth_client.post(
        "/api/v1/auth/register",
        json={"email": "short@example.com", "password": "abc"},
    )
    assert resp.status_code == 422  # Pydantic validation


async def test_login_success(auth_client: AsyncClient):
    # Register
    await auth_client.post(
        "/api/v1/auth/register",
        json={"email": "login@example.com", "password": "StrongP@ss1"},
    )
    # Login
    resp = await auth_client.post(
        "/api/v1/auth/login",
        json={"email": "login@example.com", "password": "StrongP@ss1"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["ok"] is True
    assert "access_token" in data["data"]


async def test_login_wrong_password(auth_client: AsyncClient):
    await auth_client.post(
        "/api/v1/auth/register",
        json={"email": "wrongpw@example.com", "password": "StrongP@ss1"},
    )
    resp = await auth_client.post(
        "/api/v1/auth/login",
        json={"email": "wrongpw@example.com", "password": "WrongPassword"},
    )
    assert resp.status_code == 401


async def test_login_nonexistent_user(auth_client: AsyncClient):
    resp = await auth_client.post(
        "/api/v1/auth/login",
        json={"email": "nobody@example.com", "password": "whatever"},
    )
    assert resp.status_code == 401


async def test_refresh_token(auth_client: AsyncClient):
    # Register to get tokens
    reg_resp = await auth_client.post(
        "/api/v1/auth/register",
        json={"email": "refresh@example.com", "password": "StrongP@ss1"},
    )
    refresh_token = reg_resp.json()["data"]["refresh_token"]

    # Refresh
    resp = await auth_client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["ok"] is True
    assert "access_token" in data["data"]


async def test_refresh_with_access_token_fails(auth_client: AsyncClient):
    reg_resp = await auth_client.post(
        "/api/v1/auth/register",
        json={"email": "badrefresh@example.com", "password": "StrongP@ss1"},
    )
    access_token = reg_resp.json()["data"]["access_token"]

    resp = await auth_client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": access_token},  # Wrong token type
    )
    assert resp.status_code == 401


async def test_refresh_with_invalid_token(auth_client: AsyncClient):
    resp = await auth_client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": "invalid.token.here"},
    )
    assert resp.status_code == 401
