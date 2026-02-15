from typing import TYPE_CHECKING
import uuid
from sqlalchemy import String, DateTime, func, Text, ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from applytrack.db.base import Base

if TYPE_CHECKING:
    from .company import Company
    from .application import Application

class RemoteType(str, enum.Enum):
    onsite = "onsite"
    hybrid = "hybrid"
    remote = "remote"

class JobSource(str, enum.Enum):
    linkedin = "linkedin"
    indeed = "indeed"
    company = "company"
    other = "other"

class JobPosting(Base):
    __tablename__ = "job_postings"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    company_id: Mapped[str | None] = mapped_column(String, ForeignKey("companies.id"), nullable=True)
    
    title: Mapped[str] = mapped_column(String, index=True)
    location: Mapped[str | None] = mapped_column(String, nullable=True)
    remote_type: Mapped[RemoteType] = mapped_column(Enum(RemoteType), default=RemoteType.onsite)
    
    posting_url: Mapped[str | None] = mapped_column(String, nullable=True)
    source: Mapped[JobSource] = mapped_column(Enum(JobSource), default=JobSource.other)
    
    description_raw: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    
    company: Mapped["Company"] = relationship("Company", back_populates="job_postings")
    applications: Mapped[list["Application"]] = relationship("Application", back_populates="job_posting")
