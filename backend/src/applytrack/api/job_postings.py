from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from applytrack.db.session import get_db
from applytrack.db.models.user import User
from applytrack.db.models.job_posting import JobPosting, RemoteType, JobSource
from applytrack.schemas.application import JobPostingCreate, JobPostingResponse
from applytrack.api.deps import get_current_user

router = APIRouter()

@router.post("/", response_model=JobPostingResponse)
async def create_job_posting(
    job_in: JobPostingCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    # Determine source from URL (simplistic)
    source = JobSource.other
    if "linkedin.com" in job_in.url:
        source = JobSource.linkedin
    elif "indeed.com" in job_in.url:
        source = JobSource.indeed
    
    # Check if posting already exists by URL? Maybe not strict unique constraint, but good for hygiene.
    # For now, just create new.
    
    job = JobPosting(
        posting_url=job_in.url,
        description_raw=job_in.description,
        title=job_in.title or "Unknown Role",
        source=source,
        # Default others
    )
    db.add(job)
    await db.commit()
    await db.refresh(job)
    return job
