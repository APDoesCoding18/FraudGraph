import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey, text, Table
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database.postgres import Base

case_alerts = Table(
    "case_alerts",
    Base.metadata,
    Column("case_id", UUID(as_uuid=True), ForeignKey("cases.id"), primary_key=True),
    Column("alert_id", UUID(as_uuid=True), ForeignKey("alerts.id"), primary_key=True)
)

case_accounts = Table(
    "case_accounts",
    Base.metadata,
    Column("case_id", UUID(as_uuid=True), ForeignKey("cases.id"), primary_key=True),
    Column("account_id", UUID(as_uuid=True), ForeignKey("accounts.id"), primary_key=True)
)

case_transactions = Table(
    "case_transactions",
    Base.metadata,
    Column("case_id", UUID(as_uuid=True), ForeignKey("cases.id"), primary_key=True),
    Column("transaction_id", UUID(as_uuid=True), ForeignKey("transactions.id"), primary_key=True)
)

class Case(Base):
    __tablename__ = "cases"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    investigator_id = Column(UUID(as_uuid=True), ForeignKey("investigators.id"), nullable=True, index=True)
    status = Column(String, nullable=False, default="OPEN") # OPEN, UNDER_REVIEW, CLOSED
    created_at = Column(DateTime(timezone=True), server_default=text("now()"), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=text("now()"), nullable=False)
    
    investigator = relationship("Investigator")
    alerts = relationship("Alert", secondary=case_alerts)
    accounts = relationship("Account", secondary=case_accounts)
    transactions = relationship("Transaction", secondary=case_transactions)
    notes = relationship("CaseNote", back_populates="case", cascade="all, delete-orphan")
