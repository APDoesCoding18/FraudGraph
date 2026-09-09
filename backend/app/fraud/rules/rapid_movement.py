from typing import Any
from app.fraud.rules.base import FraudRule
from app.events.schemas import TransactionEvent

class RapidFundMovementRule(FraudRule):
    @property
    def rule_code(self) -> str:
        return "RAPID_FUND_MOVEMENT"

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
            
        # Expected interface: check if this account received funds recently, 
        # and count outgoing transfers within 5 minutes of that receipt.
        # Since this event IS an outgoing transfer, we check if the sender received funds
        # recently (e.g. within 5 mins) and if they have >= 2 OTHER outgoing transfers
        # in the last 5 mins (making this the 3rd one).
        
        has_recent_incoming = await redis_client.has_incoming_funds(event.sender_account_id, window_seconds=300)
        if not has_recent_incoming:
            return False
            
        # Count outgoing including this one, so if count is already 2, this makes it 3.
        # But this event isn't in Redis yet. So we check if past count >= 2.
        past_outgoing_count = await redis_client.count_outgoing_transactions(event.sender_account_id, window_seconds=300)
        
        return past_outgoing_count >= 2
