from typing import Any
from app.fraud.rules.base import FraudRule
from app.events.schemas import TransactionEvent

class HighValueTransactionRule(FraudRule):
    @property
    def rule_code(self) -> str:
        return "HIGH_VALUE_TRANSACTION"

    @property
    def severity(self) -> str:
        return "MEDIUM"

    @property
    def score(self) -> int:
        return 20

    async def evaluate(self, event: TransactionEvent, **kwargs: Any) -> bool:
        return event.amount >= 500000.0
