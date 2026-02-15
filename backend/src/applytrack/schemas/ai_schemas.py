from typing import Literal, List, Optional
from pydantic import BaseModel, Field

class EvidenceItem(BaseModel):
    id: str
    source: Literal["job_description", "profile", "memory"]
    text: str

class ParsedJD(BaseModel):
    title: str
    seniority: Optional[str] = None
    must_have_skills: List[str] = Field(default_factory=list)
    nice_to_have_skills: List[str] = Field(default_factory=list)
    responsibilities: List[str] = Field(default_factory=list)
    keywords: List[str] = Field(default_factory=list)
    evidence: List[EvidenceItem] = Field(default_factory=list)

class MatchItem(BaseModel):
    item: str
    evidence_refs: List[str] = Field(default_factory=list)

class MatchResult(BaseModel):
    match_score: int = Field(ge=0, le=100)
    strong_matches: List[MatchItem] = Field(default_factory=list)
    missing_skills: List[MatchItem] = Field(default_factory=list)
    tailored_angle: str
    do_not_claim: List[str] = Field(default_factory=list)
    evidence: List[EvidenceItem] = Field(default_factory=list)

class CVBullet(BaseModel):
    bullet: str
    evidence_refs: List[str] = Field(default_factory=list)

class TailoredCVBullets(BaseModel):
    selected_projects: List[str] = Field(default_factory=list)
    bullet_suggestions: List[CVBullet] = Field(default_factory=list)
    do_not_claim: List[str] = Field(default_factory=list)
    evidence: List[EvidenceItem] = Field(default_factory=list)

from datetime import datetime
from applytrack.db.models.ai_output import AIOutputKind

class AITaskResponse(BaseModel):
    task_id: str
    status: str
    result: Optional[dict] = None

class AIOutputResponse(BaseModel):
    id: str
    kind: AIOutputKind
    output_json: dict
    evidence_json: Optional[dict] = None
    model: str
    latency_seconds: float
    created_at: datetime
    
    class Config:
        from_attributes = True
