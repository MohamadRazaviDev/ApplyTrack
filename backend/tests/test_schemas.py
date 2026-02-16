"""Pydantic schema validation tests — no DB needed."""

import pytest
from pydantic import ValidationError

from applytrack.schemas.ai_schemas import (
    InterviewPrepResult,
    MatchResult,
    OutreachResult,
    ParsedJD,
    TailoredCV,
)
from applytrack.schemas.application import ApplicationCreate
from applytrack.schemas.auth import UserCreate
from applytrack.schemas.reminder import ReminderCreate

# ── Auth schemas ──


def test_user_create_valid():
    u = UserCreate(email="a@b.com", password="test")
    assert u.email == "a@b.com"


def test_user_create_invalid_email():
    with pytest.raises(ValidationError):
        UserCreate(email="not-an-email", password="test")


# ── Application schemas ──


def test_application_create_defaults():
    a = ApplicationCreate(company_name="X", role_title="Y")
    assert a.status.value == "not_applied"
    assert a.priority.value == "medium"
    assert a.notes == ""


def test_application_create_invalid_status():
    with pytest.raises(ValidationError):
        ApplicationCreate(company_name="X", role_title="Y", status="invalid")


# ── Reminder schemas ──


def test_reminder_create():
    r = ReminderCreate(text="Follow up", due_at="2026-03-01T10:00:00Z")
    assert r.text == "Follow up"


# ── AI schemas ──


def test_parsed_jd_validates():
    data = {
        "role_title": "SWE",
        "must_have_skills": [{"name": "Python"}],
        "responsibilities": ["Code"],
        "keywords": ["backend"],
    }
    parsed = ParsedJD.model_validate(data)
    assert parsed.role_title == "SWE"
    assert len(parsed.must_have_skills) == 1


def test_match_result_score_bounds():
    valid = MatchResult(match_score=78, strong_matches=[], gaps=[])
    assert valid.match_score == 78

    with pytest.raises(ValidationError):
        MatchResult(match_score=101, strong_matches=[], gaps=[])

    with pytest.raises(ValidationError):
        MatchResult(match_score=-1, strong_matches=[], gaps=[])


def test_tailored_cv_validates():
    cv = TailoredCV(
        tailored_summary="Summary",
        bullet_suggestions=[{"bullet": "Did X", "evidence": {"source": "profile", "text": "Y"}}],
        top_keywords=["Python"],
    )
    assert len(cv.bullet_suggestions) == 1
    assert cv.bullet_suggestions[0].evidence.source == "profile"


def test_outreach_result_validates():
    o = OutreachResult(linkedin_message="Hi", email_message="Subject: Hello")
    assert o.linkedin_message == "Hi"


def test_interview_prep_validates():
    ip = InterviewPrepResult(
        likely_questions=["Q1"],
        checklist=["Prepare"],
        suggested_stories=[
            {
                "question": "Q",
                "suggested_answer": "A",
                "evidence": {"source": "profile", "text": "E"},
            }
        ],
    )
    assert len(ip.suggested_stories) == 1
