"""Profile endpoint tests."""

import pytest
from conftest import register_and_login
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_read_profile(client: AsyncClient):
    _, headers = await register_and_login(client)
    resp = await client.get("/api/v1/profile/", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    # Profile is auto-created on registration with blank fields
    assert "id" in data
    assert data["headline"] is None


@pytest.mark.asyncio
async def test_update_profile(client: AsyncClient):
    _, headers = await register_and_login(client)
    resp = await client.put(
        "/api/v1/profile/",
        json={
            "headline": "Backend Engineer",
            "summary": "5 years Python",
            "skills_json": ["Python", "FastAPI", "PostgreSQL"],
            "experience_json": [
                {
                    "company": "Acme",
                    "role": "Engineer",
                    "start_date": "2020-01",
                    "bullets": ["Built APIs"],
                }
            ],
        },
        headers=headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["headline"] == "Backend Engineer"
    assert "Python" in data["skills_json"]
    assert len(data["experience_json"]) == 1


@pytest.mark.asyncio
async def test_profile_requires_auth(client: AsyncClient):
    resp = await client.get("/api/v1/profile/")
    assert resp.status_code == 401
