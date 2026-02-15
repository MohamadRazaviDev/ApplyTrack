from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from applytrack.db.session import get_db
from applytrack.db.models.user import User
from applytrack.db.models.application import Application
from applytrack.api.deps import get_current_user
from applytrack.schemas.ai_schemas import AITaskResponse
from applytrack.workers.tasks_ai import task_parse_jd, task_match, task_tailor_cv

router = APIRouter()

@router.post("/applications/{application_id}/parse-jd", response_model=AITaskResponse)
async def trigger_parse_jd(
    application_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    # Verify ownership
    result = await db.execute(select(Application).where(Application.id == application_id, Application.user_id == current_user.id))
    app = result.scalars().first()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    
    # Trigger task
    task = task_parse_jd.delay(application_id)
    return {"task_id": task.id, "status": "submitted"}

@router.post("/applications/{application_id}/match", response_model=AITaskResponse)
async def trigger_match(
    application_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    result = await db.execute(select(Application).where(Application.id == application_id, Application.user_id == current_user.id))
    app = result.scalars().first()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")

    task = task_match.delay(application_id)
    return {"task_id": task.id, "status": "submitted"}

@router.post("/applications/{application_id}/tailor-cv", response_model=AITaskResponse)
async def trigger_tailor_cv(
    application_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    result = await db.execute(select(Application).where(Application.id == application_id, Application.user_id == current_user.id))
    app = result.scalars().first()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")

    task = task_tailor_cv.delay(application_id)
    return {"task_id": task.id, "status": "submitted"}
