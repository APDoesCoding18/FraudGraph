import pytest
from unittest.mock import AsyncMock
from uuid import uuid4
from app.schemas.alert import AlertCreate
from app.common.enums import RiskLevel
from app.repositories.alert import create_alert

@pytest.mark.asyncio
async def test_alert_not_created_if_score_below_25():
    mock_db = AsyncMock()
    
    alert_data = AlertCreate(
        transaction_id=uuid4(),
        risk_score=20,
        risk_level=RiskLevel.LOW,
        triggered_rules=["HIGH_VALUE_TRANSACTION"]
    )
    
    alert = await create_alert(mock_db, alert_data)
    
    assert alert is None
    mock_db.add.assert_not_called()

@pytest.mark.asyncio
async def test_alert_created_if_score_25_or_above():
    mock_db = AsyncMock()
    
    alert_data = AlertCreate(
        transaction_id=uuid4(),
        risk_score=45,
        risk_level=RiskLevel.MEDIUM,
        triggered_rules=["HIGH_VALUE_TRANSACTION", "HIGH_TRANSACTION_VELOCITY"]
    )
    
    alert = await create_alert(mock_db, alert_data)
    
    assert alert is not None
    assert alert.risk_score == 45
    mock_db.add.assert_called_once_with(alert)
    mock_db.flush.assert_called_once()
