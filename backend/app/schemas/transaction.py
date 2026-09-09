from pydantic import BaseModel, ConfigDict, Field
from uuid import UUID
from datetime import datetime
from typing import Optional
from app.common.enums import TransactionStatus

class TransactionCreate(BaseModel):
    id: Optional[UUID] = None
    sender_account_id: UUID
    receiver_account_id: UUID
    amount: float = Field(..., gt=0)
    currency: str = "INR"
    timestamp: datetime

class TransactionResponse(TransactionCreate):
    id: UUID
    status: TransactionStatus
    risk_score: Optional[float] = None
    
    model_config = ConfigDict(from_attributes=True)
