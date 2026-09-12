import pytest
from httpx import AsyncClient
from uuid import uuid4

@pytest.mark.asyncio
async def test_register_investigator(async_client: AsyncClient):
    email = f"test_{uuid4()}@example.com"
    payload = {
        "email": email,
        "name": "Jane Doe",
        "password": "securepassword123"
    }
    response = await async_client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == email
    assert data["name"] == "Jane Doe"
    assert "id" in data

    # Create duplicate
    response = await async_client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 409

@pytest.mark.asyncio
async def test_login_and_me(async_client: AsyncClient):
    email = f"test_login_{uuid4()}@example.com"
    password = "loginpassword123"
    payload = {
        "email": email,
        "name": "John Smith",
        "password": password
    }
    # Register first
    await async_client.post("/api/v1/auth/register", json=payload)

    # Login
    login_data = {
        "username": email,
        "password": password
    }
    response = await async_client.post("/api/v1/auth/login", data=login_data)
    assert response.status_code == 200
    token_data = response.json()
    assert "access_token" in token_data
    assert token_data["token_type"] == "bearer"
    
    access_token = token_data["access_token"]
    
    # Get current user (me)
    headers = {"Authorization": f"Bearer {access_token}"}
    me_response = await async_client.get("/api/v1/auth/me", headers=headers)
    assert me_response.status_code == 200
    me_data = me_response.json()
    assert me_data["email"] == email
    assert me_data["name"] == "John Smith"

@pytest.mark.asyncio
async def test_get_me_unauthorized(async_client: AsyncClient):
    response = await async_client.get("/api/v1/auth/me")
    assert response.status_code == 401
