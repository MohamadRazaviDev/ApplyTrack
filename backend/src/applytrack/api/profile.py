from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from applytrack.db.session import get_db
from applytrack.db.models.user import User
from applytrack.db.models.profile import Profile
from applytrack.schemas.profile import ProfileUpdate, ProfileResponse
from applytrack.api.deps import get_current_user

router = APIRouter()

@router.get("/", response_model=ProfileResponse)
async def read_profile(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    result = await db.execute(select(Profile).where(Profile.user_id == current_user.id))
    profile = result.scalars().first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile

@router.put("/", response_model=ProfileResponse)
async def update_profile(
    profile_in: ProfileUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    result = await db.execute(select(Profile).where(Profile.user_id == current_user.id))
    profile = result.scalars().first()
    
    if not profile:
        profile = Profile(user_id=current_user.id)
        db.add(profile)
        await db.commit()
    
    update_data = profile_in.model_dump(exclude_unset=True)
    
    for key, value in update_data.items():
        setattr(profile, key, value)
    
    db.add(profile)
    await db.commit()
    await db.refresh(profile)
    return profile
