"""AI endpoints: trigger background tasks, poll status."""

from typing import Annotated

from celery.result import AsyncResult
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from applytrack.api.deps import get_current_user
from applytrack.db.models.application import Application
from applytrack.db.models.user import User
from applytrack.db.session import get_db
from applytrack.schemas.ai_schemas import AITaskResponse, AITaskStatusResponse
from applytrack.workers.celery_app import celery_app
from applytrack.workers.tasks_ai import (
    task_interview_prep,
    task_match,
    task_outreach,
    task_parse_jd,
    task_tailor_cv,
)

router = APIRouter()


async def _verify_ownership(application_id: str, user: User, db: AsyncSession) -> Application:
    result = await db.execute(
        select(Application).where(
            Application.id == application_id,
            Application.user_id == user.id,
        )
    )
    app = result.scalars().first()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    return app


def _submit(task_func, application_id: str) -> AITaskResponse:
    result = task_func.delay(application_id)
    return AITaskResponse(task_id=result.id, status="submitted")


@router.post("/parse-jd/{application_id}", response_model=AITaskResponse)
async def trigger_parse_jd(
    application_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    await _verify_ownership(application_id, current_user, db)
    return _submit(task_parse_jd, application_id)


@router.post("/match/{application_id}", response_model=AITaskResponse)
async def trigger_match(
    application_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    await _verify_ownership(application_id, current_user, db)
    return _submit(task_match, application_id)


@router.post("/tailor-cv/{application_id}", response_model=AITaskResponse)
async def trigger_tailor_cv(
    application_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    await _verify_ownership(application_id, current_user, db)
    return _submit(task_tailor_cv, application_id)


@router.post("/outreach/{application_id}", response_model=AITaskResponse)
async def trigger_outreach(
    application_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    await _verify_ownership(application_id, current_user, db)
    return _submit(task_outreach, application_id)


@router.post("/interview-prep/{application_id}", response_model=AITaskResponse)
async def trigger_interview_prep(
    application_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    await _verify_ownership(application_id, current_user, db)
    return _submit(task_interview_prep, application_id)


@router.get("/tasks/{task_id}", response_model=AITaskStatusResponse)
async def poll_task(task_id: str):
    """Check the status of a Celery task.  Frontend polls this until done."""
    result = AsyncResult(task_id, app=celery_app)
    response = AITaskStatusResponse(
        task_id=task_id,
        status=result.status,
    )
    if result.ready():
        try:
            response.result = result.result if isinstance(result.result, dict) else {}
        except Exception:
            response.result = {"error": "Task failed"}
    return response
