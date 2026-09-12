from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
from typing import Optional
from app.models.investigator import Investigator
from app.schemas.investigator import InvestigatorCreate

async def create_investigator(db: AsyncSession, investigator_in: InvestigatorCreate, hashed_password: str) -> Investigator:
    db_obj = Investigator(
        email=investigator_in.email,
        name=investigator_in.name,
        hashed_password=hashed_password
    )
    db.add(db_obj)
    await db.flush()
    return db_obj

async def get_investigator(db: AsyncSession, investigator_id: UUID) -> Optional[Investigator]:
    result = await db.execute(select(Investigator).where(Investigator.id == investigator_id))
    return result.scalar_one_or_none()

async def get_investigator_by_email(db: AsyncSession, email: str) -> Optional[Investigator]:
    result = await db.execute(select(Investigator).where(Investigator.email == email))
    return result.scalar_one_or_none()
