from typing import List, Optional, Dict, Any
from pydantic import BaseModel, HttpUrl

class Project(BaseModel):
    name: str
    stack: str
    bullets: List[str]
    metrics: Optional[str] = None

class Experience(BaseModel):
    company: str
    role: str
    start_date: str
    end_date: Optional[str] = None
    bullets: List[str]

class ProfileBase(BaseModel):
    headline: Optional[str] = None
    summary: Optional[str] = None
    location: Optional[str] = None
    links_json: Optional[Dict[str, str]] = None
    skills_json: Optional[List[str]] = None
    projects_json: Optional[List[Project]] = None
    experience_json: Optional[List[Experience]] = None

class ProfileCreate(ProfileBase):
    pass

class ProfileUpdate(ProfileBase):
    pass

class ProfileResponse(ProfileBase):
    id: str
    user_id: str
    
    class Config:
        from_attributes = True
