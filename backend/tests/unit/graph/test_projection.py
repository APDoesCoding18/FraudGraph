import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4
from datetime import datetime, timezone
from app.events.schemas import TransactionEvent
from app.graph.projection import GraphProjection
from app.common.enums import RiskLevel

@pytest.fixture
def mock_driver():
    driver = AsyncMock()
    # mock session context manager
    session = AsyncMock()
    
    # handle async with self.driver.session() as session:
    session_ctx = MagicMock()
    session_ctx.__aenter__ = AsyncMock(return_value=session)
    session_ctx.__aexit__ = AsyncMock(return_value=None)
    driver.session = MagicMock(return_value=session_ctx)
    
    return driver

@pytest.fixture
def projection(mock_driver):
    return GraphProjection(mock_driver)

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
async def test_merge_account(projection, mock_driver):
    account_id = uuid4()
    await projection.merge_account(account_id)
    
    session = mock_driver.session.return_value.__aenter__.return_value
    session.run.assert_called_once()
    args, kwargs = session.run.call_args
    assert "MERGE (a:Account" in args[0]
    assert kwargs["account_id"] == str(account_id)

@pytest.mark.asyncio
async def test_merge_transaction(projection, mock_driver, transaction_event):
    await projection.merge_transaction(transaction_event, 50, RiskLevel.HIGH)
    
    session = mock_driver.session.return_value.__aenter__.return_value
    session.run.assert_called_once()
    args, kwargs = session.run.call_args
    assert "MERGE (t:Transaction" in args[0]
    assert "[:SENT]" in args[0]
    assert "[:RECEIVED_BY]" in args[0]
    
    assert kwargs["tx_id"] == str(transaction_event.transaction_id)
    assert kwargs["risk_score"] == 50
    assert kwargs["risk_level"] == RiskLevel.HIGH
