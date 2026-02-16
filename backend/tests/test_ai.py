"""AI endpoint tests.

Because the Celery-eager worker uses a synchronous SQLAlchemy session that
cannot share the same in-process SQLite connection as the async test session,
we test AI endpoints by verifying:

1. API dispatch returns 200 with a task_id.
2. Schema validation of mock outputs (covered in test_schemas.py).
3. Ownership guard returns 404 for missing apps.
"""

import pytest
from httpx import AsyncClient

from tests.conftest import register_and_login


async def _create_app_for_ai(client: AsyncClient):
    """Register, login, create an app with a JD, return (headers, app_id)."""
    _, headers = await register_and_login(client)
    await client.put(
        "/api/v1/profile/",
        json={
            "headline": "Backend Engineer",
            "summary": "5 years Python",
            "skills_json": ["Python", "FastAPI"],
        },
        headers=headers,
    )
    resp = await client.post(
        "/api/v1/applications/",
        json={
            "company_name": "TestCo",
            "role_title": "SWE",
            "job_description": "We need a Python backend engineer with 3+ years experience.",
            "status": "applied",
        },
        headers=headers,
    )
    return headers, resp.json()["id"]


@pytest.mark.asyncio
async def test_parse_jd_dispatch(client: AsyncClient):
    headers, app_id = await _create_app_for_ai(client)
    resp = await client.post(f"/api/v1/ai/parse-jd/{app_id}", headers=headers)
    assert resp.status_code == 200
    assert "task_id" in resp.json()


@pytest.mark.asyncio
async def test_match_dispatch(client: AsyncClient):
    headers, app_id = await _create_app_for_ai(client)
    resp = await client.post(f"/api/v1/ai/match/{app_id}", headers=headers)
    assert resp.status_code == 200
    assert "task_id" in resp.json()


@pytest.mark.asyncio
async def test_tailor_cv_dispatch(client: AsyncClient):
    headers, app_id = await _create_app_for_ai(client)
    resp = await client.post(f"/api/v1/ai/tailor-cv/{app_id}", headers=headers)
    assert resp.status_code == 200
    assert "task_id" in resp.json()


@pytest.mark.asyncio
async def test_outreach_dispatch(client: AsyncClient):
    headers, app_id = await _create_app_for_ai(client)
    resp = await client.post(f"/api/v1/ai/outreach/{app_id}", headers=headers)
    assert resp.status_code == 200
    assert "task_id" in resp.json()


@pytest.mark.asyncio
async def test_interview_prep_dispatch(client: AsyncClient):
    headers, app_id = await _create_app_for_ai(client)
    resp = await client.post(f"/api/v1/ai/interview-prep/{app_id}", headers=headers)
    assert resp.status_code == 200
    assert "task_id" in resp.json()


@pytest.mark.asyncio
async def test_ai_requires_ownership(client: AsyncClient):
    _, headers = await register_and_login(client)
    resp = await client.post("/api/v1/ai/parse-jd/nonexistent-id", headers=headers)
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_ai_requires_auth(client: AsyncClient):
    resp = await client.post("/api/v1/ai/parse-jd/some-id")
    assert resp.status_code == 401
