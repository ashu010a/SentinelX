from pydantic import BaseModel
from typing import List, Optional

class GraphNode(BaseModel):
    id: str
    type: str
    label: str
    risk_score: Optional[float] = None
    severity: Optional[str] = None
    metadata: dict = {}

class GraphEdge(BaseModel):
    id: str
    source: str
    target: str
    type: str
    confidence: float
    explanation: str

class SecurityGraph(BaseModel):
    nodes: List[GraphNode]
    edges: List[GraphEdge]

class RiskPath(BaseModel):
    id: str
    nodes: List[GraphNode]
    edges: List[GraphEdge]
    path_risk: float
    highest_risk_finding: str
    explanation: str
