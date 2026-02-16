"""Company schemas."""

from datetime import datetime

from pydantic import BaseModel


class CompanyCreate(BaseModel):
    name: str
    website_url: str | None = None


class CompanyResponse(BaseModel):
    id: str
    name: str
    website_url: str | None = None
    hq_location: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}
