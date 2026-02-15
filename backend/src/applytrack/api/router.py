from fastapi import APIRouter
from applytrack.api import auth, profile, companies, applications, job_postings, ai

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(profile.router, prefix="/profile", tags=["profile"])
api_router.include_router(companies.router, prefix="/companies", tags=["companies"])
api_router.include_router(job_postings.router, prefix="/job-postings", tags=["job-postings"])
api_router.include_router(applications.router, prefix="/applications", tags=["applications"])
api_router.include_router(ai.router, prefix="/ai", tags=["ai"])
