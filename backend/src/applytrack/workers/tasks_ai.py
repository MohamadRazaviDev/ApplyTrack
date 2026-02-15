import asyncio
import hashlib
import json
import logging
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from applytrack.workers.celery_app import celery_app
from applytrack.db.session import AsyncSessionLocal
from applytrack.db.models.application import Application
from applytrack.db.models.ai_output import AIOutput, AIOutputKind
from applytrack.db.models.profile import Profile
from applytrack.schemas.ai_schemas import ParsedJD, MatchResult, TailoredCVBullets
from applytrack.services.ai.prompts import build_parse_jd_prompt, build_match_prompt, build_tailor_cv_prompt
from applytrack.services.ai.client import chat_json
from applytrack.core.config import settings
import nest_asyncio

logger = logging.getLogger(__name__)

def run_async(coro):
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None
    
    if loop and loop.is_running():
        # Patch if we are in a running loop (e.g. tests)
        nest_asyncio.apply(loop)
        return loop.run_until_complete(coro)
    else:
        return asyncio.run(coro)

async def get_application_with_job(app_id: str):
    async with AsyncSessionLocal() as db:
        stmt = select(Application).where(Application.id == app_id).options(selectinload(Application.job_posting))
        result = await db.execute(stmt)
        return result.scalars().first()

async def get_profile(user_id: str):
    async with AsyncSessionLocal() as db:
        stmt = select(Profile).where(Profile.user_id == user_id)
        result = await db.execute(stmt)
        return result.scalars().first()

async def save_ai_output(app_id: str, kind: str, result: dict, latency: float, input_hash: str):
    async with AsyncSessionLocal() as db:
        output = AIOutput(
            application_id=app_id,
            kind=kind,
            input_hash=input_hash,
            output_json=result,
            model=settings.openrouter_model,
            latency_seconds=latency
        )
        db.add(output)
        await db.commit()

def _hash_input(*parts: str) -> str:
    h = hashlib.sha256()
    for p in parts:
        h.update(str(p).encode("utf-8"))
    return h.hexdigest()

@celery_app.task
def task_parse_jd(application_id: str):
    app = run_async(get_application_with_job(application_id))
    if not app or not app.job_posting or not app.job_posting.description_raw:
        return {"error": "Job description not found"}

    jd_text = app.job_posting.description_raw
    system, user = build_parse_jd_prompt(jd_text)
    
    # Mock return if we are in mock mode (handled in client)
    text, latency = chat_json(system, user)
    
    try:
        # If mock returns json dict directly (client mock fix might be needed)
        # client returns string.
        data = json.loads(text)
        # Simple validation if it matches schema broadly
        # parsed = ParsedJD.model_validate(data) 
        # For robustness, we just save what we got if it parses as JSON
    except Exception as e:
        logger.error(f"Failed to parse AI output: {e}")
        return {"error": "Invalid AI response"}

    input_hash = _hash_input(jd_text)
    run_async(save_ai_output(application_id, AIOutputKind.parse_jd, data, latency, input_hash))
    return data

@celery_app.task
def task_match(application_id: str):
    app = run_async(get_application_with_job(application_id))
    if not app: return {"error": "App not found"}
    
    profile = run_async(get_profile(app.user_id))
    if not profile: return {"error": "Profile not found"}

    # We should use parsed JD if available, otherwise raw
    # For MVP, assume we use raw JD text + Profile JSON
    jd_text = app.job_posting.description_raw or ""
    profile_data = {
        "skills": profile.skills_json,
        "projects": profile.projects_json,
        "experience": profile.experience_json
    }

    system, user = build_match_prompt(jd_text, profile_data)
    text, latency = chat_json(system, user)
    
    try:
        data = json.loads(text)
    except:
        return {"error": "Invalid JSON"}

    input_hash = _hash_input(jd_text, json.dumps(profile_data))
    run_async(save_ai_output(application_id, AIOutputKind.match, data, latency, input_hash))
    return data

@celery_app.task
def task_tailor_cv(application_id: str):
    app = run_async(get_application_with_job(application_id))
    if not app: return
    profile = run_async(get_profile(app.user_id))
    
    jd_text = app.job_posting.description_raw or ""
    profile_data = {"projects": profile.projects_json}
    
    system, user = build_tailor_cv_prompt(jd_text, profile_data)
    text, latency = chat_json(system, user)
    
    try:
        data = json.loads(text)
    except:
        return {"error": "Invalid JSON"}

    input_hash = _hash_input(jd_text, json.dumps(profile_data))
    run_async(save_ai_output(application_id, AIOutputKind.tailor_cv, data, latency, input_hash))
    return data
