from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime
from app.common.enums import AccountStatus

class AccountBase(BaseModel):
    account_number: str
    account_type: str
    status: AccountStatus
    current_balance: float

class AccountResponse(AccountBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
