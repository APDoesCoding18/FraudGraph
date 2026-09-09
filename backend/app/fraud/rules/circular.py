from typing import Any
from app.fraud.rules.base import FraudRule
from app.events.schemas import TransactionEvent

class CircularTransactionRule(FraudRule):
    @property
    def rule_code(self) -> str:
        return "CIRCULAR_TRANSACTION"

    @property
    def severity(self) -> str:
        return "CRITICAL"

    @property
    def score(self) -> int:
        return 40

    async def evaluate(self, event: TransactionEvent, **kwargs: Any) -> bool:
        graph_queries = kwargs.get("graph_queries")
        if not graph_queries:
            return False
            
        return await graph_queries.detect_circular_transactions(
            start_account=event.sender_account_id,
            end_account=event.receiver_account_id,
            min_length=2
        )
