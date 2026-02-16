"""Auth endpoint tests: register, login, /me, edge cases."""

import pytest
from httpx import AsyncClient

from tests.conftest import register_and_login


@pytest.mark.asyncio
async def test_register_returns_201(client: AsyncClient):
    resp = await client.post(
        "/api/v1/auth/register",
        json={"email": "new@test.com", "password": "Str0ng!Pass"},
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["email"] == "new@test.com"
    assert "id" in data


@pytest.mark.asyncio
async def test_register_duplicate_email(client: AsyncClient):
    await client.post(
        "/api/v1/auth/register",
        json={"email": "dup@test.com", "password": "Str0ng!Pass"},
    )
    resp = await client.post(
        "/api/v1/auth/register",
        json={"email": "dup@test.com", "password": "Str0ng!Pass"},
    )
    assert resp.status_code == 400
    assert "already exists" in resp.json()["detail"]


@pytest.mark.asyncio
async def test_login_returns_token(client: AsyncClient):
    await client.post(
        "/api/v1/auth/register",
        json={"email": "login@test.com", "password": "Str0ng!Pass"},
    )
    resp = await client.post(
        "/api/v1/auth/login",
        data={"username": "login@test.com", "password": "Str0ng!Pass"},
    )
    assert resp.status_code == 200
    assert "access_token" in resp.json()
    assert resp.json()["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_wrong_password(client: AsyncClient):
    await client.post(
        "/api/v1/auth/register",
        json={"email": "wrong@test.com", "password": "Str0ng!Pass"},
    )
    resp = await client.post(
        "/api/v1/auth/login",
        data={"username": "wrong@test.com", "password": "badpass"},
    )
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_me_returns_current_user(client: AsyncClient):
    _, headers = await register_and_login(client, "me@test.com")
    resp = await client.get("/api/v1/auth/me", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["email"] == "me@test.com"


@pytest.mark.asyncio
async def test_me_without_token(client: AsyncClient):
    resp = await client.get("/api/v1/auth/me")
    assert resp.status_code == 401
