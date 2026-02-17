"""Seed script — creates a demo user with sample data for quick testing.

Run with:  python -m applytrack.seed
"""

import asyncio
import logging

from sqlalchemy import select

from applytrack.core.security import hash_password
from applytrack.db.base import Base
from applytrack.db.models import (  # noqa: F401 — needed for metadata
    Application,
    ApplicationStatus,
    Company,
    JobPosting,
    Profile,
    Reminder,
    User,
)
from applytrack.db.session import AsyncSessionLocal, engine

log = logging.getLogger(__name__)

DEMO_EMAIL = "demo@applytrack.local"
DEMO_PASSWORD = "demo1234"


async def seed():
    # create tables if they don't exist (handy for sqlite dev)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as db:
        # skip if already seeded
        existing = await db.execute(select(User).where(User.email == DEMO_EMAIL))
        if existing.scalars().first():
            log.info("Demo user already exists, skipping seed.")
            return

        # user
        user = User(email=DEMO_EMAIL, password_hash=hash_password(DEMO_PASSWORD))
        db.add(user)
        await db.flush()

        # profile
        profile = Profile(
            user_id=user.id,
            headline="Full-Stack Developer",
            summary=(
                "I build web apps with Python and TypeScript."
                " Interested in backend systems, APIs,"
                " and developer tooling."
            ),
            skills_json=[
                "Python",
                "TypeScript",
                "FastAPI",
                "React",
                "PostgreSQL",
                "Docker",
                "Redis",
            ],
            projects_json=[
                {
                    "name": "ApplyTrack",
                    "stack": "FastAPI, Next.js, PostgreSQL, Celery",
                    "bullets": [
                        "Built full-stack job tracker with Kanban board and AI integration",
                        "Designed structured AI output pipeline with Pydantic validation",
                    ],
                },
                {
                    "name": "Alert AI Agent",
                    "stack": "Python, NATS, Docker",
                    "bullets": [
                        "Built real-time alert processing system with AI-powered analysis",
                        "Implemented reliable messaging with NATS JetStream",
                    ],
                },
            ],
            experience_json=[
                {
                    "company": "Freelance",
                    "role": "Backend Developer",
                    "start_date": "2023-01",
                    "end_date": None,
                    "bullets": [
                        "Delivered multiple Python backend projects for clients",
                        "Set up CI/CD pipelines and Docker deployments",
                    ],
                },
            ],
        )
        db.add(profile)

        # companies + postings + applications
        companies_data = [
            ("Acme Corp", "https://acme.example.com"),
            ("TechStart", "https://techstart.example.com"),
            ("DataFlow", "https://dataflow.example.com"),
            ("CloudBase", "https://cloudbase.example.com"),
        ]

        apps_data = [
            {
                "company_idx": 0,
                "title": "Backend Engineer",
                "description": (
                    "We are looking for a backend engineer with 3+"
                    " years of Python experience. You will build"
                    " REST APIs using FastAPI, design PostgreSQL"
                    " schemas, and work with Redis caching."
                    " Experience with Docker and CI/CD pipelines"
                    " is preferred."
                ),
                "status": ApplicationStatus.applied,
            },
            {
                "company_idx": 1,
                "title": "Full-Stack Developer",
                "description": (
                    "Join our team to build modern web applications."
                    " Must have strong React and Node.js skills."
                    " Python backend experience is a plus. We use"
                    " PostgreSQL and deploy on AWS."
                ),
                "status": ApplicationStatus.interview,
            },
            {
                "company_idx": 2,
                "title": "Python Developer",
                "description": (
                    "Looking for a Python developer to help build"
                    " our data pipeline. Experience with Celery,"
                    " Redis, and async programming. Knowledge of"
                    " FastAPI or Django required."
                ),
                "status": ApplicationStatus.not_applied,
            },
            {
                "company_idx": 3,
                "title": "DevOps Engineer",
                "description": (
                    "Manage and improve our cloud infrastructure."
                    " Strong Docker and Kubernetes skills required."
                    " Terraform and monitoring experience preferred."
                ),
                "status": ApplicationStatus.rejected,
            },
        ]

        company_objs = []
        for name, url in companies_data:
            c = Company(
                name=name,
                website_url=url,
                user_id=user.id,
            )
            db.add(c)
            company_objs.append(c)
        await db.flush()

        for item in apps_data:
            posting = JobPosting(
                company_id=company_objs[item["company_idx"]].id,
                title=item["title"],
                description_raw=item["description"],
            )
            db.add(posting)
            await db.flush()

            app = Application(
                user_id=user.id,
                job_posting_id=posting.id,
                status=item["status"],
            )
            db.add(app)

        await db.commit()
        log.info("Seeded demo user: %s / %s", DEMO_EMAIL, DEMO_PASSWORD)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(seed())
