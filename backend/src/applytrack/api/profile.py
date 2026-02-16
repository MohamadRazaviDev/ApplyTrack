"""Profile endpoints: read and update the current user's profile."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from applytrack.api.deps import get_current_user
from applytrack.db.models.profile import Profile
from applytrack.db.models.user import User
from applytrack.db.session import get_db
from applytrack.schemas.profile import ProfileResponse, ProfileUpdate

router = APIRouter()


@router.get("/", response_model=ProfileResponse)
async def read_profile(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    result = await db.execute(select(Profile).where(Profile.user_id == current_user.id))
    profile = result.scalars().first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile


@router.put("/", response_model=ProfileResponse)
async def update_profile(
    body: ProfileUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    result = await db.execute(select(Profile).where(Profile.user_id == current_user.id))
    profile = result.scalars().first()

    if not profile:
        profile = Profile(user_id=current_user.id)
        db.add(profile)

    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(profile, field, value)

    await db.commit()
    await db.refresh(profile)
    return profile
