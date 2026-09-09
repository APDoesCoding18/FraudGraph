from pydantic import BaseModel, EmailStr, ConfigDict
from uuid import UUID
from datetime import datetime

class InvestigatorBase(BaseModel):
    email: EmailStr
    name: str

class InvestigatorCreate(InvestigatorBase):
    pass

class InvestigatorResponse(InvestigatorBase):
    id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
