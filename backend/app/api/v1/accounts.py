from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import List

from app.api.deps import get_db
from app.schemas.account import AccountResponse
from app.schemas.transaction import TransactionResponse
from app.repositories import account as account_repo
from app.repositories import transaction as transaction_repo

router = APIRouter()

@router.get("/{account_id}", response_model=AccountResponse)
async def get_account(
    account_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    account = await account_repo.get_account(db, account_id)
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found"
        )
    return account

@router.get("/{account_id}/transactions", response_model=List[TransactionResponse])
async def get_account_transactions(
    account_id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db)
):
    account = await account_repo.get_account(db, account_id)
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found"
        )
    transactions = await transaction_repo.get_transactions(db, skip=skip, limit=limit, account_id=account_id)
    return transactions
