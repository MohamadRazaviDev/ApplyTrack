"""Reminder schemas."""

from datetime import datetime

from pydantic import BaseModel


class ReminderCreate(BaseModel):
    text: str
    due_at: datetime


class ReminderUpdate(BaseModel):
    done: bool | None = None
    text: str | None = None
    due_at: datetime | None = None


class ReminderResponse(BaseModel):
    id: str
    application_id: str
    user_id: str
    text: str
    due_at: datetime
    done: bool
    created_at: datetime

    model_config = {"from_attributes": True}
