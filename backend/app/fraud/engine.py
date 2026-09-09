from typing import List, Any
import asyncio
from app.events.schemas import TransactionEvent
from app.fraud.result import RuleResult
from app.fraud.rules import (
    HighValueTransactionRule,
    HighTransactionVelocityRule,
    RapidFundMovementRule,
    DormantAccountActivationRule,
    NewBeneficiaryLargeTransferRule,
    FanInFanOutRule,
    CircularTransactionRule,
    MuleAccountPatternRule,
    SuspiciousTransactionClusterRule
)
from app.fraud.scoring import calculate_risk
from app.common.enums import RiskLevel

class FraudEngine:
    def __init__(self):
        self.rules = [
            HighValueTransactionRule(),
            HighTransactionVelocityRule(),
            RapidFundMovementRule(),
            DormantAccountActivationRule(),
            NewBeneficiaryLargeTransferRule(),
            FanInFanOutRule(),
            CircularTransactionRule(),
            MuleAccountPatternRule(),
            SuspiciousTransactionClusterRule()
        ]

    async def evaluate_transaction(self, event: TransactionEvent, **kwargs: Any) -> tuple[List[RuleResult], int, RiskLevel]:
        """
        Runs all fraud rules concurrently against the transaction event.
        Returns the list of rule results, the calculated total score, and the risk level.
        """
        tasks = [rule.execute(event, **kwargs) for rule in self.rules]
        results = await asyncio.gather(*tasks)
        
        score, level = calculate_risk(results)
        
        return results, score, level

fraud_engine = FraudEngine()
