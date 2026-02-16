"""Pydantic schemas for every AI output type.

Each schema enforces strict structure so the frontend always knows what to
expect — no free-text AI responses.  Evidence snippets link claims back to
specific lines in the job description or profile.
"""

from datetime import datetime

from pydantic import BaseModel, Field

from applytrack.db.models.ai_output import AIOutputKind

# --- shared building blocks ---


class EvidenceSnippet(BaseModel):
    """A snippet from the JD or profile that backs a specific claim."""

    source: str = Field(description="'job_description' or 'profile'")
    text: str


class SkillItem(BaseModel):
    name: str
    evidence: EvidenceSnippet | None = None


class StoryItem(BaseModel):
    question: str
    suggested_answer: str
    evidence: EvidenceSnippet | None = None


# --- A) Parse JD ---


class ParsedJD(BaseModel):
    role_title: str
    seniority: str | None = None
    must_have_skills: list[SkillItem] = Field(default_factory=list)
    nice_to_have_skills: list[SkillItem] = Field(default_factory=list)
    responsibilities: list[str] = Field(default_factory=list)
    keywords: list[str] = Field(default_factory=list)
    questions_to_ask: list[str] = Field(default_factory=list)


# --- B) Match profile to JD ---


class MatchItem(BaseModel):
    item: str
    evidence: EvidenceSnippet | None = None


class MatchResult(BaseModel):
    match_score: int = Field(ge=0, le=100)
    strong_matches: list[MatchItem] = Field(default_factory=list)
    gaps: list[MatchItem] = Field(default_factory=list)
    recommended_projects: list[str] = Field(default_factory=list)
    recommended_experience: list[str] = Field(default_factory=list)


# --- C) Tailor CV ---


class CVBullet(BaseModel):
    bullet: str
    evidence: EvidenceSnippet | None = None


class TailoredCV(BaseModel):
    tailored_summary: str = ""
    bullet_suggestions: list[CVBullet] = Field(default_factory=list)
    top_keywords: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


# --- D) Outreach ---


class OutreachResult(BaseModel):
    linkedin_message: str = ""
    email_message: str = ""


# --- E) Interview Prep ---


class InterviewPrepResult(BaseModel):
    likely_questions: list[str] = Field(default_factory=list)
    checklist: list[str] = Field(default_factory=list)
    suggested_stories: list[StoryItem] = Field(default_factory=list)


# --- API response wrappers ---


class AITaskResponse(BaseModel):
    task_id: str
    status: str


class AITaskStatusResponse(BaseModel):
    task_id: str
    status: str  # PENDING, STARTED, SUCCESS, FAILURE
    result: dict | None = None


class AIOutputResponse(BaseModel):
    id: str
    kind: AIOutputKind
    output_json: dict
    evidence_json: dict | None = None
    model: str
    latency_seconds: float
    created_at: datetime

    model_config = {"from_attributes": True}
