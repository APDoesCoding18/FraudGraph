import uuid
from sqlalchemy import Column, String, DateTime, Numeric, ForeignKey, text, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database.postgres import Base

class Transaction(Base):
    __tablename__ = "transactions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sender_account_id = Column(UUID(as_uuid=True), ForeignKey("accounts.id"), nullable=False, index=True)
    receiver_account_id = Column(UUID(as_uuid=True), ForeignKey("accounts.id"), nullable=False, index=True)
    amount = Column(Numeric(18, 4), nullable=False)
    currency = Column(String, nullable=False, default="INR")
    timestamp = Column(DateTime(timezone=True), nullable=False)
    status = Column(String, nullable=False) # RECEIVED, PROCESSING, PROCESSED, FAILED
    risk_score = Column(Float, nullable=True)
    
    sender = relationship("Account", foreign_keys=[sender_account_id])
    receiver = relationship("Account", foreign_keys=[receiver_account_id])
