"""Prompt builders for each AI module.

Each function returns (system_prompt, user_prompt) ready for the chat client.
The system prompt embeds the target Pydantic schema so the model knows the
exact JSON shape we expect.
"""

import json

from applytrack.schemas.ai_schemas import (
    InterviewPrepResult,
    MatchResult,
    OutreachResult,
    ParsedJD,
    TailoredCV,
)

EVIDENCE_RULES = """
Rules you must follow:
1. Every skill or claim MUST include an evidence snippet showing WHERE in the
   source text you found it.  Use {"source": "job_description", "text": "..."} or
   {"source": "profile", "text": "..."}.
2. If you cannot find supporting evidence for something, set evidence to null.
3. Do NOT invent facts — only reference information present in the inputs.
4. The output MUST be valid JSON matching the schema below exactly.
"""


def _schema_hint(model_cls) -> str:
    return json.dumps(model_cls.model_json_schema(), indent=2)


def build_parse_jd_prompt(jd_text: str) -> tuple[str, str]:
    system = (
        "You are a job-description parser.  Extract structured information "
        "from the provided job description.\n\n"
        + EVIDENCE_RULES
        + "\nJSON schema:\n"
        + _schema_hint(ParsedJD)
    )
    user = f"Parse this job description:\n\n{jd_text}"
    return system, user


def build_match_prompt(jd_text: str, profile_data: dict) -> tuple[str, str]:
    system = (
        "You are a career-match analyst.  Compare the candidate profile "
        "against the job description and evaluate the fit.\n\n"
        + EVIDENCE_RULES
        + "\nJSON schema:\n"
        + _schema_hint(MatchResult)
    )
    user = (
        "[JOB DESCRIPTION]\n"
        + jd_text
        + "\n\n[CANDIDATE PROFILE]\n"
        + json.dumps(profile_data, default=str)
    )
    return system, user


def build_tailor_cv_prompt(jd_text: str, profile_data: dict) -> tuple[str, str]:
    system = (
        "You are a resume-tailoring assistant.  Suggest a tailored summary, "
        "bullet points, and keywords based on the candidate profile and job "
        "description.\n\n" + EVIDENCE_RULES + "\nJSON schema:\n" + _schema_hint(TailoredCV)
    )
    user = (
        "[JOB DESCRIPTION]\n"
        + jd_text
        + "\n\n[CANDIDATE PROFILE]\n"
        + json.dumps(profile_data, default=str)
    )
    return system, user


def build_outreach_prompt(jd_text: str, profile_data: dict) -> tuple[str, str]:
    system = (
        "You are a professional outreach writer.  Draft a LinkedIn message "
        "and an email to reach out about the role.  Keep it concise and "
        "genuine — avoid sounding generic.\n\n"
        "JSON schema:\n" + _schema_hint(OutreachResult)
    )
    user = (
        "[JOB DESCRIPTION]\n"
        + jd_text
        + "\n\n[CANDIDATE PROFILE]\n"
        + json.dumps(profile_data, default=str)
    )
    return system, user


def build_interview_prep_prompt(jd_text: str, profile_data: dict) -> tuple[str, str]:
    system = (
        "You are an interview-preparation coach.  Generate likely interview "
        "questions, a preparation checklist, and suggested STAR stories the "
        "candidate can use.\n\n"
        + EVIDENCE_RULES
        + "\nJSON schema:\n"
        + _schema_hint(InterviewPrepResult)
    )
    user = (
        "[JOB DESCRIPTION]\n"
        + jd_text
        + "\n\n[CANDIDATE PROFILE]\n"
        + json.dumps(profile_data, default=str)
    )
    return system, user
