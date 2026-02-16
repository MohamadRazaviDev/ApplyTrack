"""AI client — talks to OpenAI-compatible APIs or returns mock data.

The mode is controlled by settings.ai_mode:
  - "mock": returns pre-built JSON that passes full Pydantic validation.
  - "real": calls the configured provider (OpenRouter, OpenAI, etc.).
"""

import json
import logging
import time

from openai import OpenAI

from applytrack.core.config import settings

log = logging.getLogger(__name__)


def _build_client() -> OpenAI:
    return OpenAI(
        base_url=settings.ai_base_url,
        api_key=settings.ai_api_key,
        timeout=settings.ai_timeout_seconds,
    )


# ─── mock outputs ───────────────────────────────────────────────

_MOCK_PARSE_JD = {
    "role_title": "Backend Engineer",
    "seniority": "Mid-level",
    "must_have_skills": [
        {
            "name": "Python",
            "evidence": {
                "source": "job_description",
                "text": "3+ years Python experience required",
            },
        },
        {
            "name": "FastAPI",
            "evidence": {"source": "job_description", "text": "Build REST APIs using FastAPI"},
        },
        {
            "name": "PostgreSQL",
            "evidence": {
                "source": "job_description",
                "text": "Design and maintain PostgreSQL schemas",
            },
        },
    ],
    "nice_to_have_skills": [
        {
            "name": "Redis",
            "evidence": {"source": "job_description", "text": "Caching layer experience preferred"},
        },
        {"name": "Docker", "evidence": None},
    ],
    "responsibilities": [
        "Design and build scalable backend services",
        "Write automated tests and maintain CI pipelines",
        "Participate in code reviews and architectural discussions",
    ],
    "keywords": ["microservices", "REST", "async", "CI/CD", "testing"],
    "questions_to_ask": [
        "What does the on-call rotation look like?",
        "How is the team structured?",
    ],
}

_MOCK_MATCH = {
    "match_score": 78,
    "strong_matches": [
        {
            "item": "Python",
            "evidence": {
                "source": "profile",
                "text": "5 years building backend services with Python",
            },
        },
        {
            "item": "FastAPI",
            "evidence": {
                "source": "profile",
                "text": "Built ApplyTrack API using FastAPI and async SQLAlchemy",
            },
        },
    ],
    "gaps": [
        {"item": "Kubernetes", "evidence": None},
    ],
    "recommended_projects": ["ApplyTrack", "Alert AI Agent"],
    "recommended_experience": ["Backend Developer at Acme Corp"],
}

_MOCK_TAILOR_CV = {
    "tailored_summary": (
        "Backend engineer with 5 years of Python experience building"
        " production APIs. Comfortable with FastAPI, PostgreSQL,"
        " and async patterns."
    ),
    "bullet_suggestions": [
        {
            "bullet": (
                "Designed and shipped a real-time job-tracking API"
                " serving 500+ req/s using FastAPI and PostgreSQL"
            ),
            "evidence": {
                "source": "profile",
                "text": "Built ApplyTrack backend",
            },
        },
        {
            "bullet": (
                "Implemented structured AI pipelines with Pydantic"
                " validation and Celery background workers"
            ),
            "evidence": {
                "source": "profile",
                "text": "AI integration module",
            },
        },
    ],
    "top_keywords": ["Python", "FastAPI", "PostgreSQL", "async", "Celery"],
    "warnings": ["Do not claim Kubernetes experience — not found in profile"],
}

_MOCK_OUTREACH = {
    "linkedin_message": (
        "Hi — I came across the Backend Engineer role at your company"
        " and wanted to reach out. I have been building Python backend"
        " systems for a few years now, most recently a full-stack job"
        " tracker with FastAPI and Celery. I would love to learn more"
        " about the team. Happy to chat whenever works for you."
    ),
    "email_message": (
        "Subject: Backend Engineer application — quick intro\n\n"
        "Hi,\n\n"
        "I saw the Backend Engineer position and it lines up well"
        " with my background in Python, FastAPI, and PostgreSQL."
        " I have shipped production APIs and worked with async"
        " patterns and background job processing.\n\n"
        "I would welcome the chance to discuss how I could"
        " contribute. My portfolio and resume are attached."
        "\n\nBest regards"
    ),
}

_MOCK_INTERVIEW_PREP = {
    "likely_questions": [
        "Describe a time you had to debug a tricky production issue.",
        "How do you approach designing a new API from scratch?",
        "Walk me through your experience with async programming in Python.",
        "How do you handle database migrations in a production environment?",
    ],
    "checklist": [
        "Review the job description and map your experience to each requirement",
        "Prepare two STAR stories about backend debugging",
        "Be ready to whiteboard a simple system design",
        "Research the company's tech blog and recent product updates",
    ],
    "suggested_stories": [
        {
            "question": ("Tell me about a complex backend system you built"),
            "suggested_answer": (
                "I built ApplyTrack, a full-stack job tracker with"
                " FastAPI, PostgreSQL, and Celery. The trickiest"
                " part was designing the AI pipeline to run structured"
                " output validation in background tasks while keeping"
                " the API responsive."
            ),
            "evidence": {
                "source": "profile",
                "text": "ApplyTrack project",
            },
        },
    ],
}

_MOCKS = {
    "parse_jd": _MOCK_PARSE_JD,
    "match": _MOCK_MATCH,
    "tailor_cv": _MOCK_TAILOR_CV,
    "outreach": _MOCK_OUTREACH,
    "interview_prep": _MOCK_INTERVIEW_PREP,
}


def chat_json(system: str, user: str, kind: str = "") -> tuple[str, float]:
    """Send a chat completion and return (json_text, latency_seconds).

    In mock mode the *kind* parameter selects which canned response to return.
    """
    start = time.perf_counter()

    if settings.ai_mode == "mock":
        log.info("AI mock mode — returning sample output for %s", kind or "unknown")
        time.sleep(0.3)  # tiny delay so latency field isn't zero
        data = _MOCKS.get(kind, {})
        return json.dumps(data), round(time.perf_counter() - start, 3)

    # real mode
    client = _build_client()
    log.info("Calling %s (model=%s)", settings.ai_provider, settings.ai_model)
    resp = client.chat.completions.create(
        model=settings.ai_model,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        response_format={"type": "json_object"},
    )
    latency = round(time.perf_counter() - start, 3)
    text = resp.choices[0].message.content or "{}"
    return text, latency
