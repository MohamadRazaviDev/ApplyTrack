"""Application CRUD with flat creation (auto-creates company + job posting)."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from applytrack.api.deps import get_current_user
from applytrack.db.models.ai_output import AIOutput
from applytrack.db.models.application import Application
from applytrack.db.models.company import Company
from applytrack.db.models.job_posting import JobPosting
from applytrack.db.models.user import User
from applytrack.db.session import get_db
from applytrack.schemas.ai_schemas import AIOutputResponse
from applytrack.schemas.application import (
    ApplicationCreate,
    ApplicationResponse,
    ApplicationUpdate,
)

router = APIRouter()


def _app_query(user_id: str):
    """Base query scoped to a user with job_posting eagerly loaded."""
    return (
        select(Application)
        .where(Application.user_id == user_id)
        .options(selectinload(Application.job_posting).selectinload(JobPosting.company))
    )


@router.get("/", response_model=list[ApplicationResponse])
async def list_applications(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    status: str | None = Query(None, description="Filter by status"),
    search: str | None = Query(None, description="Search company or role"),
):
    stmt = _app_query(current_user.id)

    if status:
        stmt = stmt.where(Application.status == status)

    result = await db.execute(stmt.order_by(Application.updated_at.desc()))
    apps = result.scalars().all()

    if search:
        q = search.lower()
        apps = [
            a
            for a in apps
            if q in (a.job_posting.title or "").lower()
            or q
            in (
                a.job_posting.company.name if a.job_posting and a.job_posting.company else ""
            ).lower()
        ]

    return apps


@router.post("/", response_model=ApplicationResponse, status_code=201)
async def create_application(
    body: ApplicationCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    # find or create company
    result = await db.execute(select(Company).where(Company.name == body.company_name))
    company = result.scalars().first()
    if not company:
        company = Company(name=body.company_name)
        db.add(company)
        await db.flush()

    # create job posting
    posting = JobPosting(
        company_id=company.id,
        title=body.role_title,
        posting_url=body.job_url,
        description_raw=body.job_description,
    )
    db.add(posting)
    await db.flush()

    # create application
    application = Application(
        user_id=current_user.id,
        job_posting_id=posting.id,
        status=body.status,
        priority=body.priority,
        notes=body.notes,
    )
    db.add(application)
    await db.commit()

    # reload with relations
    result = await db.execute(_app_query(current_user.id).where(Application.id == application.id))
    return result.scalars().first()


@router.get("/{application_id}", response_model=ApplicationResponse)
async def read_application(
    application_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    result = await db.execute(_app_query(current_user.id).where(Application.id == application_id))
    app = result.scalars().first()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    return app


@router.patch("/{application_id}", response_model=ApplicationResponse)
async def update_application(
    application_id: str,
    body: ApplicationUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    result = await db.execute(_app_query(current_user.id).where(Application.id == application_id))
    app = result.scalars().first()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")

    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(app, field, value)

    await db.commit()
    await db.refresh(app)
    return app


@router.delete("/{application_id}", status_code=204)
async def delete_application(
    application_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    result = await db.execute(
        select(Application).where(
            Application.id == application_id,
            Application.user_id == current_user.id,
        )
    )
    app = result.scalars().first()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")

    await db.delete(app)
    await db.commit()


@router.get("/{application_id}/ai-outputs", response_model=list[AIOutputResponse])
async def list_ai_outputs(
    application_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    # verify access
    result = await db.execute(
        select(Application).where(
            Application.id == application_id,
            Application.user_id == current_user.id,
        )
    )
    if not result.scalars().first():
        raise HTTPException(status_code=404, detail="Application not found")

    result = await db.execute(
        select(AIOutput)
        .where(AIOutput.application_id == application_id)
        .order_by(AIOutput.created_at.desc())
    )
    return result.scalars().all()
