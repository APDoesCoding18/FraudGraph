from typing import Any
from app.fraud.rules.base import FraudRule
from app.events.schemas import TransactionEvent

class FanInFanOutRule(FraudRule):
    @property
    def rule_code(self) -> str:
        return "FAN_IN_FAN_OUT"

    @property
    def severity(self) -> str:
        return "HIGH"

    @property
    def score(self) -> int:
        return 30

    async def evaluate(self, event: TransactionEvent, **kwargs: Any) -> bool:
        redis_client = kwargs.get("redis_client")
        if not redis_client:
            return False
            
        # We need distinct counterparties in rolling 30 minutes.
        # We check sender's counterparties (including this new receiver)
        # And receiver's counterparties (including this new sender)
        # If either hits 5, it's FAN_IN_FAN_OUT
        
        sender_counterparties = await redis_client.count_distinct_counterparties(event.sender_account_id, window_seconds=1800)
        if (sender_counterparties + 1) >= 5: # +1 for this event
            return True
            
        receiver_counterparties = await redis_client.count_distinct_counterparties(event.receiver_account_id, window_seconds=1800)
        if (receiver_counterparties + 1) >= 5:
            return True
            
        return False
