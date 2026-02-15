from typing import Optional
from pydantic import BaseModel, HttpUrl

class CompanyBase(BaseModel):
    name: str
    website_url: Optional[str] = None
    linkedin_url: Optional[str] = None
    careers_url: Optional[str] = None
    hq_location: Optional[str] = None
    notes: Optional[str] = None

class CompanyCreate(CompanyBase):
    pass

class CompanyUpdate(CompanyBase):
    pass

class CompanyResponse(CompanyBase):
    id: str
    created_at: str
    
    class Config:
        from_attributes = True
