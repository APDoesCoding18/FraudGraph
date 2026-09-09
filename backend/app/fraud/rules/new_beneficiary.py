from typing import Any
from app.fraud.rules.base import FraudRule
from app.events.schemas import TransactionEvent

class NewBeneficiaryLargeTransferRule(FraudRule):
    @property
    def rule_code(self) -> str:
        return "NEW_BENEFICIARY_LARGE_TRANSFER"

    @property
    def severity(self) -> str:
        return "MEDIUM"

    @property
    def score(self) -> int:
        return 20

    async def evaluate(self, event: TransactionEvent, **kwargs: Any) -> bool:
        if event.amount < 100000.0:
            return False
            
        db_session = kwargs.get("db_session")
        if not db_session:
            return False
            
        from sqlalchemy import select, func
        from app.models.transaction import Transaction
        
        # Check if any transaction exists from sender to receiver
        stmt = select(func.count(Transaction.id)).where(
            Transaction.sender_account_id == event.sender_account_id,
            Transaction.receiver_account_id == event.receiver_account_id,
            Transaction.id != event.transaction_id
        )
        
        result = await db_session.execute(stmt)
        count = result.scalar_one()
        
        return count == 0
