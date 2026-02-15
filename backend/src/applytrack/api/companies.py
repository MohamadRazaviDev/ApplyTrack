from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from applytrack.db.session import get_db
from applytrack.db.models.user import User
from applytrack.db.models.company import Company
from applytrack.schemas.company import CompanyCreate, CompanyResponse, CompanyUpdate
from applytrack.api.deps import get_current_user

router = APIRouter()

@router.get("/", response_model=list[CompanyResponse])
async def read_companies(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    result = await db.execute(select(Company))
    companies = result.scalars().all()
    return companies

@router.post("/", response_model=CompanyResponse)
async def create_company(
    company_in: CompanyCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    company = Company(**company_in.model_dump())
    db.add(company)
    await db.commit()
    await db.refresh(company)
    return company

@router.put("/{company_id}", response_model=CompanyResponse)
async def update_company(
    company_id: str,
    company_in: CompanyUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    result = await db.execute(select(Company).where(Company.id == company_id))
    company = result.scalars().first()
    
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    update_data = company_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(company, key, value)
    
    db.add(company)
    await db.commit()
    await db.refresh(company)
    return company
