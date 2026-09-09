from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID
from datetime import datetime
from typing import List, Optional
from app.common.enums import AlertStatus, RiskLevel

class AlertBase(BaseModel):
    transaction_id: UUID
    risk_score: int = Field(..., ge=0, le=100)
    risk_level: RiskLevel
    triggered_rules: List[str]

class AlertCreate(AlertBase):
    pass

class AlertUpdate(BaseModel):
    status: Optional[AlertStatus] = None

class AlertResponse(AlertBase):
    id: UUID
    status: AlertStatus
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
