from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from applytrack.db.session import get_db
from applytrack.db.models.user import User
from applytrack.db.models.application import Application, ApplicationStatus
from applytrack.db.models.job_posting import JobPosting
from applytrack.db.models.ai_output import AIOutput
from applytrack.schemas.application import ApplicationCreate, ApplicationUpdate, ApplicationResponse
from applytrack.schemas.ai_schemas import AIOutputResponse
from applytrack.api.deps import get_current_user

router = APIRouter()

@router.get("/", response_model=list[ApplicationResponse])
async def read_applications(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    result = await db.execute(
        select(Application)
        .where(Application.user_id == current_user.id)
        .options(selectinload(Application.job_posting))
    )
    applications = result.scalars().all()
    return applications

@router.post("/", response_model=ApplicationResponse)
async def create_application(
    application_in: ApplicationCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    # Verify job posting exists
    result = await db.execute(select(JobPosting).where(JobPosting.id == application_in.job_posting_id))
    job_posting = result.scalars().first()
    if not job_posting:
        raise HTTPException(status_code=404, detail="Job posting not found")
        
    application = Application(
        **application_in.model_dump(),
        user_id=current_user.id
    )
    db.add(application)
    await db.commit()
    await db.refresh(application)
    
    # Reload with relations
    result = await db.execute(
        select(Application)
        .where(Application.id == application.id)
        .options(selectinload(Application.job_posting))
    )
    application = result.scalars().first()
    return application

@router.get("/{application_id}", response_model=ApplicationResponse)
async def read_application(
    application_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    result = await db.execute(
        select(Application)
        .where(Application.id == application_id, Application.user_id == current_user.id)
        .options(selectinload(Application.job_posting))
    )
    application = result.scalars().first()
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    return application

@router.patch("/{application_id}", response_model=ApplicationResponse)
async def update_application(
    application_id: str,
    application_in: ApplicationUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    result = await db.execute(
        select(Application)
        .where(Application.id == application_id, Application.user_id == current_user.id)
        .options(selectinload(Application.job_posting))
    )
    application = result.scalars().first()
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    
    update_data = application_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(application, key, value)
    
    db.add(application)
    await db.commit()
    await db.refresh(application)
    return application

@router.get("/{application_id}/ai-outputs", response_model=list[AIOutputResponse])
async def read_application_ai_outputs(
    application_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    # Verify access
    result = await db.execute(select(Application).where(Application.id == application_id, Application.user_id == current_user.id))
    app = result.scalars().first()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
        
    result = await db.execute(select(AIOutput).where(AIOutput.application_id == application_id).order_by(AIOutput.created_at.desc()))
    outputs = result.scalars().all()
    return outputs
