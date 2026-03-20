from pydantic import BaseModel
from typing import List, Optional

class ReportRequest(BaseModel):
    address: str
    reason: str
    username: str
    scam_type: str = "Unknown"
    description: str = ""

class WalletStats(BaseModel):
    transaction_count: int
    total_ether_in: float
    total_ether_out: float
    unique_interactions: int
    tornado_cash_detected: bool

class AnalysisResult(BaseModel):
    risk_score: int
    risk_level: str
    explanation: str

class ScanResponse(BaseModel):
    address: str
    chain: str
    stats: WalletStats
    analysis: AnalysisResult
    transactions: List[dict]
    peeling_chain_detected: bool = False
    community_flagged: bool = False

class LoginRequest(BaseModel):
    username: str
    password: str

class SignupRequest(BaseModel):
    username: str
    password: str
    email: str

class GraphNode(BaseModel):
    id: str
    label: str
    type: str
    value: float = 0.0

class GraphEdge(BaseModel):
    source: str
    target: str
    value: float
    interaction_count: int

class GraphResponse(BaseModel):
    nodes: List[GraphNode]
    edges: List[GraphEdge]