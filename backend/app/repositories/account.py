from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models.account import Account

async def check_accounts_exist(session: AsyncSession, account_ids: list[UUID]) -> bool:
    if not account_ids:
        return True
    
    stmt = select(func.count(Account.id)).where(Account.id.in_(account_ids))
    result = await session.execute(stmt)
    count = result.scalar_one()
    
    # Check if the number of distinct found accounts matches the unique provided ids
    return count == len(set(account_ids))

async def get_account(session: AsyncSession, account_id: UUID) -> Account | None:
    result = await session.execute(select(Account).where(Account.id == account_id))
    return result.scalar_one_or_none()
