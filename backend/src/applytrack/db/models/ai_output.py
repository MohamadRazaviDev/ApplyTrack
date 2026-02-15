import uuid
import enum
from typing import TYPE_CHECKING
from sqlalchemy import String, DateTime, func, ForeignKey, Enum, JSON, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship
from applytrack.db.base import Base

if TYPE_CHECKING:
    from .application import Application

class AIOutputKind(str, enum.Enum):
    parse_jd = "parse_jd"
    match = "match"
    tailor_cv = "tailor_cv"
    outreach = "outreach"
    interview_prep = "interview_prep"

class AIOutput(Base):
    __tablename__ = "ai_outputs"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    application_id: Mapped[str] = mapped_column(String, ForeignKey("applications.id"), index=True)
    
    kind: Mapped[AIOutputKind] = mapped_column(Enum(AIOutputKind))
    input_hash: Mapped[str] = mapped_column(String)
    
    output_json: Mapped[dict] = mapped_column(JSON)
    evidence_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    
    model: Mapped[str] = mapped_column(String)
    latency_seconds: Mapped[float] = mapped_column(Float)
    
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    
    application: Mapped["Application"] = relationship("Application", back_populates="ai_outputs")
