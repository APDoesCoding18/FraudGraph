from typing import Any
from app.fraud.rules.base import FraudRule
from app.events.schemas import TransactionEvent

class SuspiciousTransactionClusterRule(FraudRule):
    @property
    def rule_code(self) -> str:
        return "SUSPICIOUS_TRANSACTION_CLUSTER"

    @property
    def severity(self) -> str:
        return "HIGH"

    @property
    def score(self) -> int:
        return 30

    async def evaluate(self, event: TransactionEvent, **kwargs: Any) -> bool:
        graph_queries = kwargs.get("graph_queries")
        if not graph_queries:
            return False
            
        return await graph_queries.detect_suspicious_cluster(
            account_id=event.sender_account_id,
            min_accounts=5,
            min_high_risk_transactions=3
        )
