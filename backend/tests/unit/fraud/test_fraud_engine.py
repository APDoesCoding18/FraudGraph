import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4
from datetime import datetime, timezone
from app.events.schemas import TransactionEvent
from app.fraud.engine import fraud_engine
from app.common.enums import RiskLevel

@pytest.fixture
def transaction_event():
    return TransactionEvent(
        transaction_id=uuid4(),
        sender_account_id=uuid4(),
        receiver_account_id=uuid4(),
        amount=600000.0, # Triggers High Value by default
        currency="INR",
        timestamp=datetime.now(timezone.utc)
    )

@pytest.mark.asyncio
async def test_fraud_engine_high_value_only(transaction_event):
    redis_mock = AsyncMock()
    redis_mock.count_transactions.return_value = 1
    redis_mock.has_incoming_funds.return_value = False
    redis_mock.count_distinct_counterparties.return_value = 1
    redis_mock.count_distinct_incoming.return_value = 0
    redis_mock.count_distinct_outgoing.return_value = 0

    neo4j_mock = AsyncMock()
    neo4j_mock.detect_circular_path.return_value = False
    neo4j_mock.detect_suspicious_cluster.return_value = False

    db_mock = AsyncMock()
    # Mocking dormant and new beneficiary to be false
    result_mock = MagicMock()
    result_mock.scalar_one_or_none.return_value = datetime.now(timezone.utc)
    result_mock.scalar_one.return_value = 1
    db_mock.execute.return_value = result_mock

    results, score, level = await fraud_engine.evaluate_transaction(
        transaction_event,
        redis_client=redis_mock,
        neo4j_driver=neo4j_mock,
        db_session=db_mock
    )

    triggered_rules = [r for r in results if r.triggered]
    assert len(triggered_rules) == 1
    assert triggered_rules[0].rule_code == "HIGH_VALUE_TRANSACTION"
    assert triggered_rules[0].score_contribution == 20
    assert score == 20
    assert level == RiskLevel.LOW

@pytest.mark.asyncio
async def test_fraud_engine_max_score_capping(transaction_event):
    redis_mock = AsyncMock()
    redis_mock.count_transactions.return_value = 15 # Triggers velocity (25)
    redis_mock.has_incoming_funds.return_value = True # Triggers rapid movement (25)
    redis_mock.count_outgoing_transactions.return_value = 3 
    redis_mock.count_distinct_counterparties.return_value = 6 # Triggers fan out (30)
    redis_mock.count_distinct_incoming.return_value = 5 # Triggers mule (40)
    redis_mock.count_distinct_outgoing.return_value = 3

    neo4j_mock = AsyncMock()
    neo4j_mock.detect_circular_path.return_value = True # Triggers circular (40)
    neo4j_mock.detect_suspicious_cluster.return_value = True # Triggers cluster (30)

    db_mock = AsyncMock()
    # Mocking dormant and new beneficiary to be false for simplicity
    result_mock = MagicMock()
    result_mock.scalar_one_or_none.return_value = datetime.now(timezone.utc)
    result_mock.scalar_one.return_value = 1
    db_mock.execute.return_value = result_mock

    results, score, level = await fraud_engine.evaluate_transaction(
        transaction_event,
        redis_client=redis_mock,
        neo4j_driver=neo4j_mock,
        db_session=db_mock
    )

    # 20 + 25 + 25 + 30 + 40 + 40 + 30 = 210, but capped at 100
    assert score == 100
    assert level == RiskLevel.CRITICAL
