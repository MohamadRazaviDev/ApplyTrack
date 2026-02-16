"""Central API router — wires every sub-router under /api/v1."""

from fastapi import APIRouter

from applytrack.api import ai, applications, auth, companies, profile, reminders

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(profile.router, prefix="/profile", tags=["profile"])
api_router.include_router(companies.router, prefix="/companies", tags=["companies"])
api_router.include_router(applications.router, prefix="/applications", tags=["applications"])
api_router.include_router(reminders.router, tags=["reminders"])
api_router.include_router(ai.router, prefix="/ai", tags=["ai"])
