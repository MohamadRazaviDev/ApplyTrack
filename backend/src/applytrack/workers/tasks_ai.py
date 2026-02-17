"""Celery tasks for AI processing.

Each task:
  1. Loads the application + profile from the DB (sync session).
  2. Builds the prompt.
  3. Calls the AI client (mock or real).
  4. Validates the response against its Pydantic schema.
  5. Persists the AIOutput row.
  6. Returns the validated data as a dict.

We use a *synchronous* SQLAlchemy session here because Celery workers
run in their own process — no need for async, and it avoids the
nest_asyncio hack entirely.
"""

import hashlib
import json
import logging

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, selectinload, sessionmaker

from applytrack.core.config import settings
from applytrack.db.models.ai_output import AIOutput, AIOutputKind
from applytrack.db.models.application import Application
from applytrack.db.models.profile import Profile
from applytrack.schemas.ai_schemas import (
    InterviewPrepResult,
    MatchResult,
    OutreachResult,
    ParsedJD,
    TailoredCV,
)
from applytrack.services.ai.client import chat_json
from applytrack.services.ai.prompts import (
    build_interview_prep_prompt,
    build_match_prompt,
    build_outreach_prompt,
    build_parse_jd_prompt,
    build_tailor_cv_prompt,
)
from applytrack.workers.celery_app import celery_app

log = logging.getLogger(__name__)

# Synchronous engine for worker tasks.
# The URL for asyncpg needs to be swapped to psycopg2 (or plain sqlite) for sync use.
_sync_url = settings.database_url.replace("+aiosqlite", "").replace("+asyncpg", "+psycopg2")
_engine = create_engine(_sync_url, echo=False)
_SessionLocal = sessionmaker(bind=_engine, expire_on_commit=False)


def _hash_inputs(*parts: str) -> str:
    h = hashlib.sha256()
    for p in parts:
        h.update(str(p).encode())
    return h.hexdigest()[:16]


def _load_app(session: Session, app_id: str) -> Application | None:
    stmt = (
        select(Application)
        .where(Application.id == app_id)
        .options(selectinload(Application.job_posting))
    )
    return session.execute(stmt).scalars().first()


def _load_profile(session: Session, user_id: str) -> Profile | None:
    return session.execute(select(Profile).where(Profile.user_id == user_id)).scalars().first()


def _profile_dict(profile: Profile) -> dict:
    return {
        "headline": profile.headline,
        "summary": profile.summary,
        "skills": profile.skills_json or [],
        "projects": profile.projects_json or [],
        "experience": profile.experience_json or [],
    }


def _save_output(
    session: Session,
    app_id: str,
    kind: AIOutputKind,
    data: dict,
    latency: float,
    input_hash: str,
    evidence: list[dict] | None = None,
):
    output = AIOutput(
        application_id=app_id,
        kind=kind,
        input_hash=input_hash,
        output_json=data,
        evidence_json=evidence or [],
        model=settings.ai_model,
        latency_seconds=latency,
    )
    session.add(output)
    session.commit()


def _extract_evidence(data: dict) -> list[dict]:
    """Walk validated output and collect all evidence snippets."""
    evidence = []
    for key, value in data.items():
        if isinstance(value, dict) and "source" in value and "text" in value:
            evidence.append({"field": key, **value})
        elif isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    ev = item.get("evidence")
                    if isinstance(ev, dict) and ev.get("text"):
                        evidence.append(
                            {
                                "field": key,
                                **ev,
                            }
                        )
    return evidence


def _run_task(
    app_id: str,
    kind: AIOutputKind,
    prompt_builder,
    schema_cls,
    needs_profile=False,
):
    """Shared task runner used by every AI task."""
    with _SessionLocal() as session:
        app = _load_app(session, app_id)
        if not app or not app.job_posting:
            return {"error": "Application or job posting not found"}

        jd_text = app.job_posting.description_raw or ""

        profile_data = {}
        if needs_profile:
            profile = _load_profile(session, app.user_id)
            if not profile:
                return {"error": "Profile not found"}
            profile_data = _profile_dict(profile)

        # build prompt
        if needs_profile:
            system, user = prompt_builder(jd_text, profile_data)
        else:
            system, user = prompt_builder(jd_text)

        # call AI (mock or real)
        text, latency = chat_json(system, user, kind=kind.value)

        # parse + validate — failures surface as task errors
        raw = json.loads(text)
        validated = schema_cls.model_validate(raw)
        data = validated.model_dump()

        # extract evidence refs from the validated output
        evidence = _extract_evidence(data)

        input_hash = _hash_inputs(jd_text, json.dumps(profile_data))
        _save_output(
            session,
            app_id,
            kind,
            data,
            latency,
            input_hash,
            evidence=evidence,
        )
        return data


@celery_app.task
def task_parse_jd(application_id: str):
    return _run_task(
        application_id,
        AIOutputKind.parse_jd,
        build_parse_jd_prompt,
        ParsedJD,
    )


@celery_app.task
def task_match(application_id: str):
    return _run_task(
        application_id,
        AIOutputKind.match,
        build_match_prompt,
        MatchResult,
        needs_profile=True,
    )


@celery_app.task
def task_tailor_cv(application_id: str):
    return _run_task(
        application_id,
        AIOutputKind.tailor_cv,
        build_tailor_cv_prompt,
        TailoredCV,
        needs_profile=True,
    )


@celery_app.task
def task_outreach(application_id: str):
    return _run_task(
        application_id,
        AIOutputKind.outreach,
        build_outreach_prompt,
        OutreachResult,
        needs_profile=True,
    )


@celery_app.task
def task_interview_prep(application_id: str):
    return _run_task(
        application_id,
        AIOutputKind.interview_prep,
        build_interview_prep_prompt,
        InterviewPrepResult,
        needs_profile=True,
    )
