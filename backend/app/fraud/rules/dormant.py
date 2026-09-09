from typing import Any
from app.fraud.rules.base import FraudRule
from app.events.schemas import TransactionEvent

class DormantAccountActivationRule(FraudRule):
    @property
    def rule_code(self) -> str:
        return "DORMANT_ACCOUNT_ACTIVATION"

    @property
    def severity(self) -> str:
        return "HIGH"

    @property
    def score(self) -> int:
        return 25

    async def evaluate(self, event: TransactionEvent, **kwargs: Any) -> bool:
        if event.amount < 100000.0:
            return False
            
        db_session = kwargs.get("db_session")
        if not db_session:
            return False
            
        from sqlalchemy import select, func, text
        from app.models.transaction import Transaction
        
        # Check last transaction date for this account (sender)
        stmt = select(func.max(Transaction.timestamp)).where(
            (Transaction.sender_account_id == event.sender_account_id) | 
            (Transaction.receiver_account_id == event.sender_account_id)
        ).where(
            Transaction.id != event.transaction_id
        )
        
        result = await db_session.execute(stmt)
        last_tx_time = result.scalar_one_or_none()
        
        if not last_tx_time:
            # If there's literally no previous transaction, is it dormant or just new?
            # A new account might technically not have recorded transactions for 90 days if it was inactive since creation.
            # We assume no transaction = dormant if account is old, but for safety, we require a verifiable gap >= 90 days.
            # For this requirement: "no recorded transaction for >= 90 consecutive days"
            # It could mean checking account creation date if no transactions exist.
            # Let's assume if last_tx_time is None, we check account creation.
            from app.models.account import Account
            acc_stmt = select(Account.created_at).where(Account.id == event.sender_account_id)
            acc_res = await db_session.execute(acc_stmt)
            last_tx_time = acc_res.scalar_one_or_none()
            if not last_tx_time:
                return False

        delta = event.timestamp - last_tx_time
        return delta.days >= 90
