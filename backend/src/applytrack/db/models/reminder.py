import uuid
from typing import TYPE_CHECKING
from sqlalchemy import String, DateTime, func, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from applytrack.db.base import Base

if TYPE_CHECKING:
    from .application import Application

class Reminder(Base):
    __tablename__ = "reminders"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    application_id: Mapped[str] = mapped_column(String, ForeignKey("applications.id"), index=True)
    
    text: Mapped[str] = mapped_column(String)
    due_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True))
    done: Mapped[bool] = mapped_column(Boolean, default=False)
    
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    
    application: Mapped["Application"] = relationship("Application", back_populates="reminders")
