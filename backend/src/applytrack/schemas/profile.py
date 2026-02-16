"""Profile schemas."""

from pydantic import BaseModel


class ProjectItem(BaseModel):
    name: str
    stack: str
    bullets: list[str] = []
    metrics: str | None = None


class ExperienceItem(BaseModel):
    company: str
    role: str
    start_date: str
    end_date: str | None = None
    bullets: list[str] = []


class ProfileUpdate(BaseModel):
    headline: str | None = None
    summary: str | None = None
    location: str | None = None
    links_json: dict[str, str] | None = None
    skills_json: list[str] | None = None
    projects_json: list[ProjectItem] | None = None
    experience_json: list[ExperienceItem] | None = None


class ProfileResponse(BaseModel):
    id: str
    user_id: str
    headline: str | None = None
    summary: str | None = None
    location: str | None = None
    links_json: dict | None = None
    skills_json: list | None = None
    projects_json: list | None = None
    experience_json: list | None = None

    model_config = {"from_attributes": True}
