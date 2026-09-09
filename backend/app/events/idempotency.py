import logging
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.transaction import Transaction
from app.common.enums import TransactionStatus
from uuid import UUID

logger = logging.getLogger(__name__)

async def is_event_processed(session: AsyncSession, transaction_id: UUID) -> bool:
    """
    Checks if a transaction event has already been processed based on the
    Transaction's status in PostgreSQL.
    Returns True if it's already PROCESSED or FAILED.
    """
    from sqlalchemy import select
    stmt = select(Transaction).where(Transaction.id == transaction_id)
    result = await session.execute(stmt)
    tx = result.scalar_one_or_none()
    
    if not tx:
        logger.warning(f"Transaction {transaction_id} not found during idempotency check")
        return False # Can't be processed if it doesn't exist, though this is an anomaly.

    if tx.status in [TransactionStatus.PROCESSED.value, TransactionStatus.FAILED.value]:
        return True
        
    return False

async def mark_event_processing(session: AsyncSession, transaction_id: UUID):
    """
    Marks the transaction as PROCESSING.
    """
    from sqlalchemy import update
    stmt = update(Transaction).where(Transaction.id == transaction_id).values(status=TransactionStatus.PROCESSING.value)
    await session.execute(stmt)
    await session.commit()
