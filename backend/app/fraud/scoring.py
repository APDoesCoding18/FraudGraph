from typing import List, Tuple
from app.fraud.result import RuleResult
from app.common.enums import RiskLevel

def calculate_risk(rule_results: List[RuleResult]) -> Tuple[int, RiskLevel]:
    score = sum(r.score_contribution for r in rule_results if r.triggered)
    score = min(score, 100)
    
    if score < 25:
        level = RiskLevel.LOW
    elif score < 50:
        level = RiskLevel.MEDIUM
    elif score < 75:
        level = RiskLevel.HIGH
    else:
        level = RiskLevel.CRITICAL
        
    return score, level
