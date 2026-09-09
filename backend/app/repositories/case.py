from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from uuid import UUID
from typing import List, Optional

from app.models.case import Case
from app.models.case_note import CaseNote
from app.models.alert import Alert
from app.schemas.case import CaseCreate, CaseStatusUpdate, CaseNoteCreate

async def create_case(db: AsyncSession, case_data: CaseCreate) -> Case:
    # Fetch alerts to link
    alerts = []
    if case_data.alert_ids:
        stmt = select(Alert).where(Alert.id.in_(case_data.alert_ids))
        result = await db.execute(stmt)
        alerts = list(result.scalars().all())

    db_case = Case(
        investigator_id=case_data.investigator_id,
        alerts=alerts
    )
    db.add(db_case)
    await db.flush()
    return db_case

async def get_case(db: AsyncSession, case_id: UUID) -> Optional[Case]:
    stmt = select(Case).options(
        selectinload(Case.alerts),
        selectinload(Case.notes)
    ).where(Case.id == case_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()

async def get_cases(db: AsyncSession, skip: int = 0, limit: int = 100, status: Optional[str] = None) -> List[Case]:
    stmt = select(Case).order_by(Case.created_at.desc())
    if status:
        stmt = stmt.where(Case.status == status)
    stmt = stmt.offset(skip).limit(limit)
    result = await db.execute(stmt)
    return list(result.scalars().all())

async def update_case_status(db: AsyncSession, case_id: UUID, status_update: CaseStatusUpdate) -> Optional[Case]:
    case = await get_case(db, case_id)
    if not case:
        return None
    case.status = status_update.status.value
    await db.flush()
    return case

async def add_case_note(db: AsyncSession, case_id: UUID, note_data: CaseNoteCreate) -> CaseNote:
    db_note = CaseNote(
        case_id=case_id,
        investigator_id=note_data.investigator_id,
        content=note_data.content
    )
    db.add(db_note)
    await db.flush()
    return db_note
