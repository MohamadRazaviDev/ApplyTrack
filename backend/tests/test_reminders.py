"""Reminder endpoint tests."""

import pytest
from httpx import AsyncClient

from tests.conftest import register_and_login


async def _create_app_with_reminder_setup(client: AsyncClient):
    """Register, login, create an app, return (headers, app_id)."""
    _, headers = await register_and_login(client)
    resp = await client.post(
        "/api/v1/applications/",
        json={
            "company_name": "Acme",
            "role_title": "Dev",
            "status": "applied",
        },
        headers=headers,
    )
    return headers, resp.json()["id"]


@pytest.mark.asyncio
async def test_create_reminder(client: AsyncClient):
    headers, app_id = await _create_app_with_reminder_setup(client)
    resp = await client.post(
        f"/api/v1/applications/{app_id}/reminders",
        json={"text": "Follow up", "due_at": "2026-03-01T10:00:00Z"},
        headers=headers,
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["text"] == "Follow up"
    assert data["done"] is False
    assert data["application_id"] == app_id


@pytest.mark.asyncio
async def test_list_reminders(client: AsyncClient):
    headers, app_id = await _create_app_with_reminder_setup(client)
    await client.post(
        f"/api/v1/applications/{app_id}/reminders",
        json={"text": "R1", "due_at": "2026-03-01T10:00:00Z"},
        headers=headers,
    )
    await client.post(
        f"/api/v1/applications/{app_id}/reminders",
        json={"text": "R2", "due_at": "2026-03-02T10:00:00Z"},
        headers=headers,
    )
    resp = await client.get("/api/v1/reminders", headers=headers)
    assert resp.status_code == 200
    assert len(resp.json()) == 2


@pytest.mark.asyncio
async def test_list_reminders_filter_done(client: AsyncClient):
    headers, app_id = await _create_app_with_reminder_setup(client)
    r = await client.post(
        f"/api/v1/applications/{app_id}/reminders",
        json={"text": "Done one", "due_at": "2026-03-01T10:00:00Z"},
        headers=headers,
    )
    rid = r.json()["id"]
    # mark done
    await client.patch(
        f"/api/v1/reminders/{rid}",
        json={"done": True},
        headers=headers,
    )

    resp = await client.get("/api/v1/reminders?done=false", headers=headers)
    assert resp.status_code == 200
    assert len(resp.json()) == 0

    resp = await client.get("/api/v1/reminders?done=true", headers=headers)
    assert len(resp.json()) == 1


@pytest.mark.asyncio
async def test_update_reminder(client: AsyncClient):
    headers, app_id = await _create_app_with_reminder_setup(client)
    r = await client.post(
        f"/api/v1/applications/{app_id}/reminders",
        json={"text": "Original", "due_at": "2026-03-01T10:00:00Z"},
        headers=headers,
    )
    rid = r.json()["id"]

    resp = await client.patch(
        f"/api/v1/reminders/{rid}",
        json={"text": "Updated", "done": True},
        headers=headers,
    )
    assert resp.status_code == 200
    assert resp.json()["text"] == "Updated"
    assert resp.json()["done"] is True


@pytest.mark.asyncio
async def test_reminder_not_found(client: AsyncClient):
    _, headers = await register_and_login(client)
    resp = await client.patch(
        "/api/v1/reminders/nonexistent",
        json={"done": True},
        headers=headers,
    )
    assert resp.status_code == 404
