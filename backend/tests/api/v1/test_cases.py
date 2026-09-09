import pytest
from httpx import AsyncClient
from uuid import uuid4
from app.common.enums import CaseStatus

@pytest.mark.asyncio
async def test_get_cases_empty(async_client: AsyncClient):
    response = await async_client.get("/api/v1/cases")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

@pytest.mark.asyncio
async def test_get_case_not_found(async_client: AsyncClient):
    fake_id = uuid4()
    response = await async_client.get(f"/api/v1/cases/{fake_id}")
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_update_case_status_not_found(async_client: AsyncClient):
    fake_id = uuid4()
    response = await async_client.patch(
        f"/api/v1/cases/{fake_id}/status", 
        json={"status": CaseStatus.CLOSED.value}
    )
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_add_case_note_not_found(async_client: AsyncClient):
    fake_id = uuid4()
    response = await async_client.post(
        f"/api/v1/cases/{fake_id}/notes",
        json={"investigator_id": str(uuid4()), "content": "Test note"}
    )
    assert response.status_code == 404
