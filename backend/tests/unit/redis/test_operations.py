import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4
from datetime import datetime, timezone
from app.events.schemas import TransactionEvent
from app.redis.operations import RedisOperations

@pytest.fixture
def mock_redis_client():
    client = AsyncMock()
    # zcount returns an integer
    client.zcount.return_value = 5
    
    # Mock pipeline
    pipeline = AsyncMock()
    client.pipeline.return_value = pipeline
    return client

@pytest.fixture
def redis_ops(mock_redis_client):
    return RedisOperations(mock_redis_client)

@pytest.fixture
def transaction_event():
    return TransactionEvent(
        transaction_id=uuid4(),
        sender_account_id=uuid4(),
        receiver_account_id=uuid4(),
        amount=100.0,
        currency="INR",
        timestamp=datetime.now(timezone.utc)
    )

@pytest.mark.asyncio
async def test_count_transactions(redis_ops, mock_redis_client):
    account_id = uuid4()
    count = await redis_ops.count_transactions(account_id, 3600)
    
    assert count == 5
    mock_redis_client.zcount.assert_called_once()
    args = mock_redis_client.zcount.call_args[0]
    assert args[0] == f"tx_history:{account_id}"
    # args[1] is min_score, args[2] is max_score
    assert args[2] - args[1] == 3600

@pytest.mark.asyncio
async def test_record_transaction(redis_ops, mock_redis_client, transaction_event):
    await redis_ops.record_transaction(transaction_event)
    
    pipeline = mock_redis_client.pipeline.return_value
    
    # Check that it updated 7 keys: tx_history x2, outgoing_tx, outgoing, incoming, counterparties x2
    assert pipeline.zadd.call_count == 7
    assert pipeline.zremrangebyscore.call_count == 7
    assert pipeline.expire.call_count == 7
    
    pipeline.execute.assert_called_once()
    
    # Verify expire was called with 3600
    expire_args = pipeline.expire.call_args[0]
    assert expire_args[1] == 3600
