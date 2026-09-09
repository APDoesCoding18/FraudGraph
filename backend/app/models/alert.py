from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
import uuid

from app.database.postgres import Base
from app.common.enums import AlertStatus, RiskLevel

class Alert(Base):
    __tablename__ = "alerts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, server_default=text("uuid_generate_v4()"))
    transaction_id = Column(UUID(as_uuid=True), ForeignKey("transactions.id", ondelete="CASCADE"), nullable=False, unique=True)
    risk_score = Column(Integer, nullable=False)
    risk_level = Column(String(50), nullable=False)
    triggered_rules = Column(JSONB, nullable=False, default=list)
    status = Column(String(50), nullable=False, default=AlertStatus.OPEN.value)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
