from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, HttpUrl, Field
from applytrack.db.models.application import ApplicationStatus, ApplicationPriority
from applytrack.db.models.job_posting import RemoteType, JobSource

class JobPostingCreate(BaseModel):
    url: str
    description: Optional[str] = None
    title: Optional[str] = None
    company_name: Optional[str] = None

class JobPostingResponse(BaseModel):
    id: str
    title: str
    company_id: Optional[str] = None
    location: Optional[str] = None
    remote_type: RemoteType
    posting_url: Optional[str] = None
    source: JobSource
    description_raw: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

class ApplicationCreate(BaseModel):
    job_posting_id: str
    status: ApplicationStatus = ApplicationStatus.draft
    priority: ApplicationPriority = ApplicationPriority.medium
    notes: Optional[str] = None

class ApplicationUpdate(BaseModel):
    status: Optional[ApplicationStatus] = None
    priority: Optional[ApplicationPriority] = None
    notes: Optional[str] = None
    next_followup_at: Optional[datetime] = None
    salary_expectation: Optional[int] = None

class ApplicationResponse(BaseModel):
    id: str
    user_id: str
    job_posting_id: str
    status: ApplicationStatus
    priority: ApplicationPriority
    notes: str
    applied_at: Optional[datetime] = None
    next_followup_at: Optional[datetime] = None
    salary_expectation: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    
    job_posting: Optional[JobPostingResponse] = None
    
    class Config:
        from_attributes = True
