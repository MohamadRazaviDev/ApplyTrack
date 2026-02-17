"""Company endpoints — kept minimal, mostly auto-created from application flow."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from applytrack.api.deps import get_current_user
from applytrack.db.models.company import Company
from applytrack.db.models.user import User
from applytrack.db.session import get_db
from applytrack.schemas.company import CompanyResponse

router = APIRouter()


@router.get("/", response_model=list[CompanyResponse])
async def list_companies(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    result = await db.execute(
        select(Company).where(Company.user_id == current_user.id).order_by(Company.name)
    )
    return result.scalars().all()


@router.get("/{company_id}", response_model=CompanyResponse)
async def read_company(
    company_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    result = await db.execute(
        select(Company).where(
            Company.id == company_id,
            Company.user_id == current_user.id,
        )
    )
    company = result.scalars().first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return company
