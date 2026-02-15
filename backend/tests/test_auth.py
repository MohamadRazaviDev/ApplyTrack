import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_register_login(client: AsyncClient):
    # Register
    response = await client.post("/api/v1/auth/register", json={
        "email": "test@example.com",
        "password": "password123"
    })
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["email"] == "test@example.com"
    assert "id" in data
    
    # Login
    response = await client.post("/api/v1/auth/login", data={
        "username": "test@example.com",
        "password": "password123"
    })
    assert response.status_code == 200, response.text
    token_data = response.json()
    assert "access_token" in token_data
    token = token_data["access_token"]
    
    # Me
    response = await client.get("/api/v1/auth/me", headers={
        "Authorization": f"Bearer {token}"
    })
    assert response.status_code == 200, response.text
    assert response.json()["email"] == "test@example.com"
