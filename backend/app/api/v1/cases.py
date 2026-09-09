from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import List, Optional
from pydantic import BaseModel

from app.api.deps import get_db
from app.schemas.case import CaseCreate, CaseResponse, CaseStatusUpdate, CaseNoteCreate, CaseNoteResponse
from app.repositories import case as case_repo
from app.common.enums import CaseStatus

router = APIRouter()

class CaseFullResponse(CaseResponse):
    # Depending on frontend needs, we could nest alerts and notes here
    # For now, returning basic CaseResponse to match schema
    pass

@router.post("", response_model=CaseResponse, status_code=status.HTTP_201_CREATED)
async def create_case(
    case_in: CaseCreate,
    db: AsyncSession = Depends(get_db)
):
    case = await case_repo.create_case(db, case_in)
    await db.commit()
    return case

@router.get("", response_model=List[CaseResponse])
async def list_cases(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status_filter: Optional[CaseStatus] = Query(None, alias="status"),
    db: AsyncSession = Depends(get_db)
):
    status_val = status_filter.value if status_filter else None
    cases = await case_repo.get_cases(db, skip=skip, limit=limit, status=status_val)
    return cases

@router.get("/{case_id}", response_model=CaseResponse)
async def get_case(
    case_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    case = await case_repo.get_case(db, case_id)
    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Case not found"
        )
    return case

@router.patch("/{case_id}/status", response_model=CaseResponse)
async def update_case_status(
    case_id: UUID,
    status_update: CaseStatusUpdate,
    db: AsyncSession = Depends(get_db)
):
    case = await case_repo.update_case_status(db, case_id, status_update)
    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Case not found"
        )
    await db.commit()
    return case

@router.post("/{case_id}/notes", response_model=CaseNoteResponse, status_code=status.HTTP_201_CREATED)
async def add_case_note(
    case_id: UUID,
    note_in: CaseNoteCreate,
    db: AsyncSession = Depends(get_db)
):
    # Verify case exists
    case = await case_repo.get_case(db, case_id)
    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Case not found"
        )
    note = await case_repo.add_case_note(db, case_id, note_in)
    await db.commit()
    return note
