import pytest
import asyncio
import sys
from typing import AsyncGenerator
from httpx import AsyncClient, ASGITransport

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from app.main import app

from unittest.mock import AsyncMock

@pytest.fixture(autouse=True)
def mock_kafka_producer(monkeypatch):
    from app.events.producer import kafka_producer
    mock_publish = AsyncMock()
    monkeypatch.setattr(kafka_producer, "publish_transaction_event", mock_publish)
    return mock_publish

@pytest.fixture
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac
