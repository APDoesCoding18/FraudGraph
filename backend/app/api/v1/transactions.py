from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import List, Optional
from sqlalchemy.exc import IntegrityError

from app.api.deps import get_db
from app.schemas.transaction import TransactionCreate, TransactionResponse
from app.repositories import transaction as transaction_repo
from app.repositories import account as account_repo

router = APIRouter()

@router.post("", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
async def create_transaction(
    tx_data: TransactionCreate,
    db: AsyncSession = Depends(get_db)
):
    # Idempotency check if id is provided
    if tx_data.id:
        existing_tx = await transaction_repo.get_transaction(db, tx_data.id)
        if existing_tx:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Transaction with this ID already exists"
            )

    # Validate accounts exist
    accounts_to_check = [tx_data.sender_account_id, tx_data.receiver_account_id]
    accounts_exist = await account_repo.check_accounts_exist(db, accounts_to_check)
    if not accounts_exist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sender or receiver account not found"
        )
        
    try:
        new_tx = await transaction_repo.create_transaction(db, tx_data)
        
        # Publish to Kafka
        from app.events.producer import kafka_producer
        from app.events.schemas import TransactionEvent
        
        event = TransactionEvent(
            transaction_id=new_tx.id,
            sender_account_id=new_tx.sender_account_id,
            receiver_account_id=new_tx.receiver_account_id,
            amount=float(new_tx.amount),
            currency=new_tx.currency,
            timestamp=new_tx.timestamp
        )
        await kafka_producer.publish_transaction_event(event)
        
        return new_tx
    except IntegrityError:
        # Fallback for concurrent idempotency failure if unique constraint on ID fails at DB level
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Transaction with this ID already exists"
        )

@router.get("", response_model=List[TransactionResponse])
async def get_transactions(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[str] = Query(None),
    account_id: Optional[UUID] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    transactions = await transaction_repo.get_transactions(
        db, skip=skip, limit=limit, status=status, account_id=account_id
    )
    return transactions

@router.get("/{transaction_id}", response_model=TransactionResponse)
async def get_transaction(
    transaction_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    tx = await transaction_repo.get_transaction(db, transaction_id)
    if not tx:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found"
        )
    return tx
