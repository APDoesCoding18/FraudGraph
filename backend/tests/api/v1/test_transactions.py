import pytest
from httpx import AsyncClient
import uuid
from datetime import datetime, timezone
from app.common.enums import TransactionStatus

# Helper to format datetime for JSON serialization
def get_utc_now_iso():
    return datetime.now(timezone.utc).isoformat()

@pytest.mark.asyncio
async def test_create_transaction_success(async_client: AsyncClient, db_session):
    # Setup test accounts
    from app.models.account import Account
    sender_id = uuid.uuid4()
    receiver_id = uuid.uuid4()
    
    sender = Account(id=sender_id, account_number=f"ACC-S-{sender_id}")
    receiver = Account(id=receiver_id, account_number=f"ACC-R-{receiver_id}")
    
    db_session.add(sender)
    db_session.add(receiver)
    await db_session.commit()

    tx_id = uuid.uuid4()
    payload = {
        "id": str(tx_id),
        "sender_account_id": str(sender_id),
        "receiver_account_id": str(receiver_id),
        "amount": 1500.0,
        "currency": "INR",
        "timestamp": get_utc_now_iso()
    }

    response = await async_client.post("/api/v1/transactions", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["id"] == str(tx_id)
    assert data["amount"] == 1500.0
    assert data["status"] == TransactionStatus.RECEIVED.value

@pytest.mark.asyncio
async def test_create_transaction_invalid_amount(async_client: AsyncClient):
    payload = {
        "sender_account_id": str(uuid.uuid4()),
        "receiver_account_id": str(uuid.uuid4()),
        "amount": -50.0,
        "currency": "INR",
        "timestamp": get_utc_now_iso()
    }
    response = await async_client.post("/api/v1/transactions", json=payload)
    assert response.status_code == 422 # Pydantic validation error

@pytest.mark.asyncio
async def test_create_transaction_nonexistent_accounts(async_client: AsyncClient):
    payload = {
        "sender_account_id": str(uuid.uuid4()),
        "receiver_account_id": str(uuid.uuid4()),
        "amount": 100.0,
        "currency": "INR",
        "timestamp": get_utc_now_iso()
    }
    response = await async_client.post("/api/v1/transactions", json=payload)
    assert response.status_code == 404
    assert response.json()["detail"] == "Sender or receiver account not found"

@pytest.mark.asyncio
async def test_create_transaction_duplicate_id(async_client: AsyncClient, db_session):
    # Setup accounts
    from app.models.account import Account
    acc_id = uuid.uuid4()
    acc = Account(id=acc_id, account_number=f"ACC-DUP-{acc_id}")
    db_session.add(acc)
    await db_session.commit()

    tx_id = uuid.uuid4()
    payload = {
        "id": str(tx_id),
        "sender_account_id": str(acc_id),
        "receiver_account_id": str(acc_id),
        "amount": 200.0,
        "currency": "INR",
        "timestamp": get_utc_now_iso()
    }

    # First request should succeed
    resp1 = await async_client.post("/api/v1/transactions", json=payload)
    assert resp1.status_code == 201

    # Second request with same ID should fail
    resp2 = await async_client.post("/api/v1/transactions", json=payload)
    assert resp2.status_code == 409

@pytest.mark.asyncio
async def test_get_transaction_lookup(async_client: AsyncClient, db_session):
    # Setup accounts and a transaction directly
    from app.models.account import Account
    from app.models.transaction import Transaction
    acc_id = uuid.uuid4()
    db_session.add(Account(id=acc_id, account_number=f"ACC-LOOK-{acc_id}"))
    
    tx_id = uuid.uuid4()
    tx = Transaction(
        id=tx_id,
        sender_account_id=acc_id,
        receiver_account_id=acc_id,
        amount=500.0,
        currency="INR",
        timestamp=datetime.now(timezone.utc),
        status=TransactionStatus.RECEIVED.value
    )
    db_session.add(tx)
    await db_session.commit()

    # Look it up
    response = await async_client.get(f"/api/v1/transactions/{tx_id}")
    assert response.status_code == 200
    assert response.json()["id"] == str(tx_id)

@pytest.mark.asyncio
async def test_get_transactions_pagination_and_filtering(async_client: AsyncClient, db_session):
    from app.models.account import Account
    from app.models.transaction import Transaction
    acc1_id = uuid.uuid4()
    acc2_id = uuid.uuid4()
    db_session.add_all([
        Account(id=acc1_id, account_number=f"ACC-P1-{acc1_id}"),
        Account(id=acc2_id, account_number=f"ACC-P2-{acc2_id}")
    ])
    
    # Create 3 transactions
    txs = []
    for i in range(3):
        txs.append(Transaction(
            id=uuid.uuid4(),
            sender_account_id=acc1_id,
            receiver_account_id=acc2_id,
            amount=10.0 * (i+1),
            currency="INR",
            timestamp=datetime.now(timezone.utc),
            status=TransactionStatus.RECEIVED.value
        ))
    db_session.add_all(txs)
    await db_session.commit()

    # Test filtering by account
    resp_filter = await async_client.get(f"/api/v1/transactions?account_id={acc1_id}")
    assert resp_filter.status_code == 200
    assert len(resp_filter.json()) >= 3 # could be more if other tests ran

    # Test pagination
    resp_page = await async_client.get(f"/api/v1/transactions?account_id={acc1_id}&limit=2&skip=0")
    assert resp_page.status_code == 200
    assert len(resp_page.json()) == 2
