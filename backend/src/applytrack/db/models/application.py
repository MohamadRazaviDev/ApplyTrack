from typing import TYPE_CHECKING
import uuid
import enum
from sqlalchemy import String, DateTime, func, Text, ForeignKey, Enum, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from applytrack.db.base import Base

if TYPE_CHECKING:
    from .user import User
    from .job_posting import JobPosting
    from .reminder import Reminder
    from .ai_output import AIOutput
    from .activity_event import ActivityEvent

class ApplicationStatus(str, enum.Enum):
    draft = "draft"
    applied = "applied"
    hr_screen = "hr_screen"
    tech_screen = "tech_screen"
    take_home = "take_home"
    onsite = "onsite"
    offer = "offer"
    rejected = "rejected"
    withdrawn = "withdrawn"

class ApplicationPriority(str, enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"

class Application(Base):
    __tablename__ = "applications"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String, ForeignKey("users.id"), index=True)
    job_posting_id: Mapped[str] = mapped_column(String, ForeignKey("job_postings.id"), index=True)
    
    status: Mapped[ApplicationStatus] = mapped_column(Enum(ApplicationStatus), default=ApplicationStatus.draft)
    priority: Mapped[ApplicationPriority] = mapped_column(Enum(ApplicationPriority), default=ApplicationPriority.medium)
    
    notes: Mapped[str] = mapped_column(Text, default="")
    applied_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    next_followup_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    salary_expectation: Mapped[int | None] = mapped_column(Integer, nullable=True)

    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    user: Mapped["User"] = relationship("User", back_populates="applications")
    job_posting: Mapped["JobPosting"] = relationship("JobPosting", back_populates="applications")
    reminders: Mapped[list["Reminder"]] = relationship("Reminder", back_populates="application", cascade="all, delete-orphan")
    ai_outputs: Mapped[list["AIOutput"]] = relationship("AIOutput", back_populates="application", cascade="all, delete-orphan")
    activity_events: Mapped[list["ActivityEvent"]] = relationship("ActivityEvent", back_populates="application", cascade="all, delete-orphan")
