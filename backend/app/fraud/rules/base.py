from abc import ABC, abstractmethod
from typing import Any
from app.events.schemas import TransactionEvent
from app.fraud.result import RuleResult

class FraudRule(ABC):
    @property
    @abstractmethod
    def rule_code(self) -> str:
        pass

    @property
    @abstractmethod
    def severity(self) -> str:
        pass

    @property
    @abstractmethod
    def score(self) -> int:
        pass

    @abstractmethod
    async def evaluate(self, event: TransactionEvent, **kwargs: Any) -> bool:
        """
        Evaluate the transaction event against the rule logic.
        Returns True if the rule is triggered, False otherwise.
        kwargs can contain database sessions, Redis clients, Neo4j drivers, etc.
        """
        pass

    async def execute(self, event: TransactionEvent, **kwargs: Any) -> RuleResult:
        triggered = await self.evaluate(event, **kwargs)
        return RuleResult(
            rule_code=self.rule_code,
            triggered=triggered,
            severity=self.severity,
            score_contribution=self.score if triggered else 0
        )
