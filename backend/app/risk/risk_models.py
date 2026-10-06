from pydantic import BaseModel
from typing import Optional, List, Dict

class FindingRiskInput(BaseModel):
    severity: str
    cvss: Optional[float] = 0.0
    epss: Optional[float] = 0.0
    kev: bool = False
    internet_exposed: bool = False
    asset_criticality: str = "medium"
    confidence: str = "certain"

class RiskResult(BaseModel):
    score: float
    category: str
    factors: Dict[str, float]
    explanation: str
    policy_version: str
