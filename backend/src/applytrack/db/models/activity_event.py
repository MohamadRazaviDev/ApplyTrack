"""Activity event log for an application timeline."""

import enum
import uuid
from typing import TYPE_CHECKING

from sqlalchemy import JSON, DateTime, Enum, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from applytrack.db.base import Base

if TYPE_CHECKING:
    from applytrack.db.models.application import Application


class ActivityEventType(str, enum.Enum):
    status_changed = "status_changed"
    note_added = "note_added"
    ai_requested = "ai_requested"
    ai_ready = "ai_ready"
    reminder_created = "reminder_created"
    reminder_done = "reminder_done"


class ActivityEvent(Base):
    __tablename__ = "activity_events"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    application_id: Mapped[str] = mapped_column(String, ForeignKey("applications.id"), index=True)

    type: Mapped[ActivityEventType] = mapped_column(Enum(ActivityEventType))
    payload_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    application: Mapped["Application"] = relationship(
        "Application", back_populates="activity_events"
    )
