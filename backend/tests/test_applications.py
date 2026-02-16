"""Application CRUD endpoint tests."""

import pytest
from httpx import AsyncClient

from tests.conftest import register_and_login


async def _create_app(client: AsyncClient, headers: dict, **overrides) -> dict:
    """Helper to create an application with sensible defaults."""
    payload = {
        "company_name": "Acme Corp",
        "role_title": "Backend Engineer",
        "job_url": "https://example.com/job",
        "job_description": "Must have Python skills.",
        "status": "applied",
        "priority": "high",
        "notes": "Looks promising",
    }
    payload.update(overrides)
    resp = await client.post("/api/v1/applications/", json=payload, headers=headers)
    assert resp.status_code == 201, resp.text
    return resp.json()


@pytest.mark.asyncio
async def test_create_application(client: AsyncClient):
    _, headers = await register_and_login(client)
    data = await _create_app(client, headers)

    assert data["status"] == "applied"
    assert data["priority"] == "high"
    assert data["notes"] == "Looks promising"
    # Flat creation should have nested job_posting with company
    assert data["job_posting"]["title"] == "Backend Engineer"
    assert data["job_posting"]["company"]["name"] == "Acme Corp"


@pytest.mark.asyncio
async def test_list_applications(client: AsyncClient):
    _, headers = await register_and_login(client)
    await _create_app(client, headers)
    await _create_app(client, headers, company_name="Other Inc", role_title="SRE")

    resp = await client.get("/api/v1/applications/", headers=headers)
    assert resp.status_code == 200
    assert len(resp.json()) == 2


@pytest.mark.asyncio
async def test_list_applications_filter_by_status(client: AsyncClient):
    _, headers = await register_and_login(client)
    await _create_app(client, headers, status="applied")
    await _create_app(client, headers, status="interview", company_name="B")

    resp = await client.get("/api/v1/applications/?status=interview", headers=headers)
    assert resp.status_code == 200
    apps = resp.json()
    assert len(apps) == 1
    assert apps[0]["status"] == "interview"


@pytest.mark.asyncio
async def test_list_applications_search(client: AsyncClient):
    _, headers = await register_and_login(client)
    await _create_app(client, headers, company_name="Google")
    await _create_app(client, headers, company_name="Meta")

    resp = await client.get("/api/v1/applications/?search=google", headers=headers)
    assert resp.status_code == 200
    assert len(resp.json()) == 1


@pytest.mark.asyncio
async def test_read_application(client: AsyncClient):
    _, headers = await register_and_login(client)
    created = await _create_app(client, headers)

    resp = await client.get(f"/api/v1/applications/{created['id']}", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["id"] == created["id"]


@pytest.mark.asyncio
async def test_update_application(client: AsyncClient):
    _, headers = await register_and_login(client)
    created = await _create_app(client, headers)

    resp = await client.patch(
        f"/api/v1/applications/{created['id']}",
        json={"status": "interview", "notes": "First round scheduled"},
        headers=headers,
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "interview"
    assert resp.json()["notes"] == "First round scheduled"


@pytest.mark.asyncio
async def test_delete_application(client: AsyncClient):
    _, headers = await register_and_login(client)
    created = await _create_app(client, headers)

    resp = await client.delete(f"/api/v1/applications/{created['id']}", headers=headers)
    assert resp.status_code == 204

    # Verify it's gone
    resp = await client.get(f"/api/v1/applications/{created['id']}", headers=headers)
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_application_not_found(client: AsyncClient):
    _, headers = await register_and_login(client)
    resp = await client.get("/api/v1/applications/nonexistent-id", headers=headers)
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_applications_require_auth(client: AsyncClient):
    resp = await client.get("/api/v1/applications/")
    assert resp.status_code == 401
