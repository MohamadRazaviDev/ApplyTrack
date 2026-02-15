import uuid
from typing import TYPE_CHECKING
from sqlalchemy import String, ForeignKey, JSON, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from applytrack.db.base import Base

if TYPE_CHECKING:
    from .user import User

class Profile(Base):
    __tablename__ = "profiles"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String, ForeignKey("users.id"), unique=True, index=True)
    
    headline: Mapped[str | None] = mapped_column(String, nullable=True)
    summary: Mapped[str | None] = mapped_column(String, nullable=True)
    location: Mapped[str | None] = mapped_column(String, nullable=True)
    
    links_json: Mapped[dict | None] = mapped_column(JSON, default=dict)
    skills_json: Mapped[list[str] | None] = mapped_column(JSON, default=list)
    projects_json: Mapped[list[dict] | None] = mapped_column(JSON, default=list)
    experience_json: Mapped[list[dict] | None] = mapped_column(JSON, default=list)

    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    user: Mapped["User"] = relationship("User", back_populates="profile")
