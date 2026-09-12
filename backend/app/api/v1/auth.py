from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, get_current_user
from app.core import security
from app.core.config import settings
from app.models.investigator import Investigator
from app.schemas.investigator import InvestigatorCreate, InvestigatorResponse
from app.schemas.token import Token
from app.repositories import investigator as investigator_repo

router = APIRouter()

@router.post("/register", response_model=InvestigatorResponse, status_code=status.HTTP_201_CREATED)
async def register_investigator(
    investigator_in: InvestigatorCreate,
    db: AsyncSession = Depends(get_db)
):
    existing = await investigator_repo.get_investigator_by_email(db, email=investigator_in.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Investigator with this email already exists"
        )
    hashed_password = security.get_password_hash(investigator_in.password)
    investigator = await investigator_repo.create_investigator(db, investigator_in, hashed_password)
    await db.commit()
    return investigator

@router.post("/login", response_model=Token)
async def login_access_token(
    db: AsyncSession = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Token:
    user = await investigator_repo.get_investigator_by_email(db, email=form_data.username)
    if not user or not user.hashed_password:
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    if not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
        
    access_token_expires = timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        subject=str(user.id), expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")

@router.get("/me", response_model=InvestigatorResponse)
async def get_current_investigator(
    current_user: Investigator = Depends(get_current_user)
):
    return current_user
