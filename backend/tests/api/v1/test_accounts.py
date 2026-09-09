import pytest
from httpx import AsyncClient
from uuid import uuid4

@pytest.mark.asyncio
async def test_get_account_not_found(async_client: AsyncClient):
    fake_id = uuid4()
    response = await async_client.get(f"/api/v1/accounts/{fake_id}")
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_get_account_transactions_not_found(async_client: AsyncClient):
    fake_id = uuid4()
    response = await async_client.get(f"/api/v1/accounts/{fake_id}/transactions")
    assert response.status_code == 404
