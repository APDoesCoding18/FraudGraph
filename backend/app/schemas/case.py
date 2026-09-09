from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime
from typing import List, Optional
from app.common.enums import CaseStatus
from app.schemas.alert import AlertResponse
from app.schemas.investigator import InvestigatorResponse

class CaseCreate(BaseModel):
    investigator_id: Optional[UUID] = None
    alert_ids: List[UUID] = []

class CaseResponse(BaseModel):
    id: UUID
    investigator_id: Optional[UUID] = None
    status: CaseStatus
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class CaseStatusUpdate(BaseModel):
    status: CaseStatus

class CaseNoteCreate(BaseModel):
    investigator_id: UUID
    content: str

class CaseNoteResponse(CaseNoteCreate):
    id: UUID
    case_id: UUID
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
