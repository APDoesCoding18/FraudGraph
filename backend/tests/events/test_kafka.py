import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from uuid import uuid4
from datetime import datetime, timezone
from app.events.schemas import TransactionEvent
from app.events.handlers import handle_transaction_event
from app.events.consumer import KafkaEventConsumer
from app.common.enums import TransactionStatus
import asyncio

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
async def test_idempotency_handler_skips_processed(transaction_event):
    mock_session = AsyncMock()
    
    with patch("app.events.handlers.is_event_processed", new_callable=AsyncMock) as mock_is_processed:
        mock_is_processed.return_value = True
        
        await handle_transaction_event(transaction_event, mock_session)
        
        # If it was skipped, it should not have marked it as processing or processed
        mock_session.execute.assert_not_called()

@pytest.mark.asyncio
async def test_idempotency_handler_processes_new(transaction_event):
    mock_session = AsyncMock()
    
    with patch("app.events.handlers.is_event_processed", new_callable=AsyncMock) as mock_is_processed, \
         patch("app.events.handlers.mark_event_processing", new_callable=AsyncMock) as mock_mark, \
         patch("app.events.handlers.redis_ops.record_transaction", new_callable=AsyncMock), \
         patch("app.events.handlers.fraud_engine.evaluate_transaction", new_callable=AsyncMock) as mock_fraud, \
         patch("app.events.handlers.neo4j_projection", new_callable=AsyncMock):
         
        mock_is_processed.return_value = False
        mock_fraud.return_value = ([], 0, TransactionStatus.PROCESSED) # Mock low score to skip alert
        
        await handle_transaction_event(transaction_event, mock_session)
        
        mock_mark.assert_called_once_with(mock_session, transaction_event.transaction_id)
        mock_session.commit.assert_called()

@pytest.mark.asyncio
async def test_consumer_dead_letter_on_exhaustion(transaction_event):
    consumer = KafkaEventConsumer()
    consumer.consumer = AsyncMock() # mock the underlying aiokafka consumer
    
    mock_msg = MagicMock()
    mock_msg.value = transaction_event.model_dump()
    
    with patch("app.events.consumer.handle_transaction_event", new_callable=AsyncMock) as mock_handle:
        # Force it to fail every time
        mock_handle.side_effect = Exception("Simulated processing failure")
        
        # Also mock sleep so tests don't take forever backing off
        with patch("asyncio.sleep", new_callable=AsyncMock):
            await consumer.process_message(mock_msg)
            
        assert mock_handle.call_count == 3 # MAX_RETRIES = 3
        consumer.consumer.commit.assert_called_once() # It must still commit so it doesn't block the queue
