"""Reminder endpoints: create, list, update."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from applytrack.api.deps import get_current_user
from applytrack.db.models.application import Application
from applytrack.db.models.reminder import Reminder
from applytrack.db.models.user import User
from applytrack.db.session import get_db
from applytrack.schemas.reminder import ReminderCreate, ReminderResponse, ReminderUpdate

router = APIRouter()


@router.post(
    "/applications/{application_id}/reminders",
    response_model=ReminderResponse,
    status_code=201,
)
async def create_reminder(
    application_id: str,
    body: ReminderCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    # verify the user owns the application
    result = await db.execute(
        select(Application).where(
            Application.id == application_id,
            Application.user_id == current_user.id,
        )
    )
    if not result.scalars().first():
        raise HTTPException(status_code=404, detail="Application not found")

    reminder = Reminder(
        application_id=application_id,
        user_id=current_user.id,
        text=body.text,
        due_at=body.due_at,
    )
    db.add(reminder)
    await db.commit()
    await db.refresh(reminder)
    return reminder


@router.get("/reminders", response_model=list[ReminderResponse])
async def list_reminders(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    done: bool | None = None,
):
    stmt = select(Reminder).where(Reminder.user_id == current_user.id)
    if done is not None:
        stmt = stmt.where(Reminder.done == done)
    stmt = stmt.order_by(Reminder.due_at.asc())

    result = await db.execute(stmt)
    return result.scalars().all()


@router.patch("/reminders/{reminder_id}", response_model=ReminderResponse)
async def update_reminder(
    reminder_id: str,
    body: ReminderUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    result = await db.execute(
        select(Reminder).where(
            Reminder.id == reminder_id,
            Reminder.user_id == current_user.id,
        )
    )
    reminder = result.scalars().first()
    if not reminder:
        raise HTTPException(status_code=404, detail="Reminder not found")

    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(reminder, field, value)

    await db.commit()
    await db.refresh(reminder)
    return reminder
