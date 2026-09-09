from typing import Any
from app.fraud.rules.base import FraudRule
from app.events.schemas import TransactionEvent

class HighTransactionVelocityRule(FraudRule):
    @property
    def rule_code(self) -> str:
        return "HIGH_TRANSACTION_VELOCITY"

    @property
    def severity(self) -> str:
        return "HIGH"

    @property
    def score(self) -> int:
        return 25

    async def evaluate(self, event: TransactionEvent, **kwargs: Any) -> bool:
        redis_client = kwargs.get("redis_client")
        if not redis_client:
            return False
            
        # Clean internal interface matching requirements:
        # Expected: redis_client.count_transactions(account_id, window_seconds)
        count = await redis_client.count_transactions(event.sender_account_id, window_seconds=600) # 10 mins
        return count >= 10
