import pytest
from pydantic import ValidationError
from uuid import uuid4
from datetime import datetime
from app.schemas.transaction import TransactionCreate
from app.schemas.common import PaginationParams
from app.schemas.alert import AlertStatusUpdate
from app.common.enums import AlertStatus

def test_valid_transaction_create():
    tx = TransactionCreate(
        sender_account_id=uuid4(),
        receiver_account_id=uuid4(),
        amount=100.50,
        timestamp=datetime.now()
    )
    assert tx.amount == 100.50

def test_invalid_uuid_transaction():
    with pytest.raises(ValidationError):
        TransactionCreate(
            sender_account_id="invalid-uuid",
            receiver_account_id=uuid4(),
            amount=100.0,
            timestamp=datetime.now()
        )

def test_invalid_amount_transaction():
    with pytest.raises(ValidationError):
        TransactionCreate(
            sender_account_id=uuid4(),
            receiver_account_id=uuid4(),
            amount=-50.0, # invalid amount
            timestamp=datetime.now()
        )

def test_valid_pagination():
    page = PaginationParams(page=2, size=20)
    assert page.page == 2
    assert page.size == 20

def test_invalid_enum_status():
    with pytest.raises(ValidationError):
        AlertStatusUpdate(status="UNKNOWN_STATUS")
