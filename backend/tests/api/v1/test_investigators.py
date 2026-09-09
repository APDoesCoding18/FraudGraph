import pytest
from httpx import AsyncClient
from uuid import uuid4

@pytest.mark.asyncio
async def test_create_investigator(async_client: AsyncClient):
    # Depending on test database state, we use a unique email
    email = f"test_{uuid4()}@example.com"
    payload = {
        "email": email,
        "name": "Jane Doe"
    }
    response = await async_client.post("/api/v1/investigators", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == email
    assert data["name"] == "Jane Doe"
    assert "id" in data

    # Create duplicate
    response = await async_client.post("/api/v1/investigators", json=payload)
    assert response.status_code == 409

@pytest.mark.asyncio
async def test_get_investigator_not_found(async_client: AsyncClient):
    fake_id = uuid4()
    response = await async_client.get(f"/api/v1/investigators/{fake_id}")
    assert response.status_code == 404
