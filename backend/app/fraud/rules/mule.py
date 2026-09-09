from typing import Any
from app.fraud.rules.base import FraudRule
from app.events.schemas import TransactionEvent

class MuleAccountPatternRule(FraudRule):
    @property
    def rule_code(self) -> str:
        return "MULE_ACCOUNT_PATTERN"

    @property
    def severity(self) -> str:
        return "CRITICAL"

    @property
    def score(self) -> int:
        return 40

    async def evaluate(self, event: TransactionEvent, **kwargs: Any) -> bool:
        redis_client = kwargs.get("redis_client")
        if not redis_client:
            return False
            
        # ">=5 distinct incoming AND >=3 distinct outgoing in 1 hour combined with onward movement"
        # Since this event is a transaction, it's either an incoming to receiver or outgoing from sender.
        # We check both the sender and receiver.
        
        # Check Sender (who is doing an outgoing tx)
        sender_in = await redis_client.count_distinct_incoming(event.sender_account_id, window_seconds=3600)
        sender_out = await redis_client.count_distinct_outgoing(event.sender_account_id, window_seconds=3600)
        
        if sender_in >= 5 and (sender_out + 1) >= 3:
            return True
            
        # Check Receiver (who is getting an incoming tx)
        receiver_in = await redis_client.count_distinct_incoming(event.receiver_account_id, window_seconds=3600)
        receiver_out = await redis_client.count_distinct_outgoing(event.receiver_account_id, window_seconds=3600)
        
        if (receiver_in + 1) >= 5 and receiver_out >= 3:
            return True
            
        return False
