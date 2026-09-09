from pydantic import BaseModel

class RuleResult(BaseModel):
    rule_code: str
    triggered: bool
    severity: str
    score_contribution: int
