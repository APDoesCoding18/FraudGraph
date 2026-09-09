import pytest
from httpx import AsyncClient
from unittest.mock import patch
from uuid import uuid4

@pytest.mark.asyncio
@patch("app.api.v1.assistant.generate_response")
async def test_assistant_chat_no_case(mock_generate, async_client: AsyncClient):
    mock_generate.return_value = "Mocked LLM response"
    
    payload = {
        "query": "What is the fraud trend?",
        "history": []
    }
    
    response = await async_client.post("/api/v1/assistant/chat", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["answer"] == "Mocked LLM response"
    assert len(data["sources"]) == 0

@pytest.mark.asyncio
async def test_assistant_chat_case_not_found(async_client: AsyncClient):
    payload = {
        "case_id": str(uuid4()),
        "query": "Summarize this case.",
        "history": []
    }
    
    response = await async_client.post("/api/v1/assistant/chat", json=payload)
    assert response.status_code == 404
