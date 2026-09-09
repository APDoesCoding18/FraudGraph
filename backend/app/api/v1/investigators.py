from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.api.deps import get_db
from app.schemas.investigator import InvestigatorCreate, InvestigatorResponse
from app.repositories import investigator as investigator_repo

router = APIRouter()

@router.post("", response_model=InvestigatorResponse, status_code=status.HTTP_201_CREATED)
async def create_investigator(
    investigator_in: InvestigatorCreate,
    db: AsyncSession = Depends(get_db)
):
    existing = await investigator_repo.get_investigator_by_email(db, email=investigator_in.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Investigator with this email already exists"
        )
        
    investigator = await investigator_repo.create_investigator(db, investigator_in)
    await db.commit()
    return investigator

@router.get("/{investigator_id}", response_model=InvestigatorResponse)
async def get_investigator(
    investigator_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    investigator = await investigator_repo.get_investigator(db, investigator_id)
    if not investigator:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Investigator not found"
        )
    return investigator
