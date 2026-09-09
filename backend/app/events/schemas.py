from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

class TransactionEvent(BaseModel):
    transaction_id: UUID
    sender_account_id: UUID
    receiver_account_id: UUID
    amount: float
    currency: str
    timestamp: datetime
