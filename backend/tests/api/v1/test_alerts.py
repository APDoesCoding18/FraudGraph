import pytest
from httpx import AsyncClient
from uuid import uuid4
from app.common.enums import AlertStatus

@pytest.mark.asyncio
async def test_get_alerts_empty(async_client: AsyncClient):
    response = await async_client.get("/api/v1/alerts")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

@pytest.mark.asyncio
async def test_get_alert_not_found(async_client: AsyncClient):
    fake_id = uuid4()
    response = await async_client.get(f"/api/v1/alerts/{fake_id}")
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_update_alert_status_not_found(async_client: AsyncClient):
    fake_id = uuid4()
    response = await async_client.patch(
        f"/api/v1/alerts/{fake_id}/status", 
        json={"status": AlertStatus.INVESTIGATING.value}
    )
    assert response.status_code == 404
