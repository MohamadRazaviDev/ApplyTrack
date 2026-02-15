import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_applications_flow(client: AsyncClient):
    # 1. Register/Login
    await client.post("/api/v1/auth/register", json={
        "email": "appuser@example.com",
        "password": "password123"
    })
    login_res = await client.post("/api/v1/auth/login", data={
        "username": "appuser@example.com",
        "password": "password123"
    })
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Create Job Posting
    job_res = await client.post("/api/v1/job-postings/", json={
        "url": "https://example.com/job",
        "title": "Software Engineer",
        "description": "Must have Python skills."
    }, headers=headers)
    assert job_res.status_code == 200, job_res.text
    job_id = job_res.json()["id"]

    # 3. Create Application
    app_res = await client.post("/api/v1/applications/", json={
        "job_posting_id": job_id,
        "status": "applied",
        "priority": "high",
        "notes": "Looks promising"
    }, headers=headers)
    assert app_res.status_code == 200, app_res.text
    app_data = app_res.json()
    assert app_data["status"] == "applied"
    assert app_data["job_posting"]["title"] == "Software Engineer"
    
    # 4. List Applications
    list_res = await client.get("/api/v1/applications/", headers=headers)
    assert list_res.status_code == 200
    assert len(list_res.json()) == 1

    # 5. Trigger AI Parse
    app_id = app_data["id"]
    ai_res = await client.post(f"/api/v1/ai/applications/{app_id}/parse-jd", headers=headers)
    assert ai_res.status_code == 200
    
    # 6. Check AI Outputs (assuming task_always_eager=True)
    outputs_res = await client.get(f"/api/v1/applications/{app_id}/ai-outputs", headers=headers)
    assert outputs_res.status_code == 200
    outputs = outputs_res.json()
    assert len(outputs) >= 1
    assert outputs[0]["kind"] == "parse_jd"
    assert outputs[0]["output_json"]["title"] == "Mock Job Title"
