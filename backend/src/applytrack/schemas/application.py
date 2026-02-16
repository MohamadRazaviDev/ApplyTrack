"""Application and job posting schemas."""

from datetime import datetime

from pydantic import BaseModel

from applytrack.db.models.application import ApplicationPriority, ApplicationStatus
from applytrack.db.models.job_posting import JobSource, RemoteType
from applytrack.schemas.company import CompanyResponse

# --- job posting ---


class JobPostingResponse(BaseModel):
    id: str
    title: str
    company_id: str | None = None
    location: str | None = None
    remote_type: RemoteType
    posting_url: str | None = None
    source: JobSource
    description_raw: str | None = None
    created_at: datetime

    company: CompanyResponse | None = None

    model_config = {"from_attributes": True}


# --- application ---


class ApplicationCreate(BaseModel):
    """Flat creation payload — company + job posting are created automatically."""

    company_name: str
    role_title: str
    job_url: str | None = None
    job_description: str | None = None
    status: ApplicationStatus = ApplicationStatus.not_applied
    priority: ApplicationPriority = ApplicationPriority.medium
    notes: str = ""


class ApplicationUpdate(BaseModel):
    status: ApplicationStatus | None = None
    priority: ApplicationPriority | None = None
    notes: str | None = None
    next_followup_at: datetime | None = None
    salary_expectation: int | None = None


class ApplicationResponse(BaseModel):
    id: str
    user_id: str
    job_posting_id: str
    status: ApplicationStatus
    priority: ApplicationPriority
    notes: str
    applied_at: datetime | None = None
    next_followup_at: datetime | None = None
    salary_expectation: int | None = None
    created_at: datetime
    updated_at: datetime

    job_posting: JobPostingResponse | None = None

    model_config = {"from_attributes": True}
