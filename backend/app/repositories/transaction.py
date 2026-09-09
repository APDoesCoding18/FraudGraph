from uuid import UUID
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.transaction import Transaction
from app.schemas.transaction import TransactionCreate
from app.common.enums import TransactionStatus
import uuid

async def create_transaction(session: AsyncSession, tx_data: TransactionCreate) -> Transaction:
    db_transaction = Transaction(
        id=tx_data.id if tx_data.id else uuid.uuid4(),
        sender_account_id=tx_data.sender_account_id,
        receiver_account_id=tx_data.receiver_account_id,
        amount=tx_data.amount,
        currency=tx_data.currency,
        timestamp=tx_data.timestamp,
        status=TransactionStatus.RECEIVED.value
    )
    session.add(db_transaction)
    await session.commit()
    await session.refresh(db_transaction)
    return db_transaction

async def get_transaction(session: AsyncSession, tx_id: UUID) -> Optional[Transaction]:
    result = await session.execute(select(Transaction).where(Transaction.id == tx_id))
    return result.scalar_one_or_none()

async def get_transactions(
    session: AsyncSession, 
    skip: int = 0, 
    limit: int = 100, 
    status: Optional[str] = None,
    account_id: Optional[UUID] = None
) -> List[Transaction]:
    stmt = select(Transaction)
    
    if status:
        stmt = stmt.where(Transaction.status == status)
    if account_id:
        stmt = stmt.where(
            (Transaction.sender_account_id == account_id) | 
            (Transaction.receiver_account_id == account_id)
        )
        
    stmt = stmt.offset(skip).limit(limit)
    result = await session.execute(stmt)
    return list(result.scalars().all())
