import time
import json
import logging
from openai import OpenAI
from applytrack.core.config import settings

logger = logging.getLogger(__name__)

def _client() -> OpenAI:
    return OpenAI(
        base_url=settings.openrouter_base_url,
        api_key=settings.openrouter_api_key,
        timeout=settings.openrouter_timeout_seconds,
    )

def chat_json(system: str, user: str) -> tuple[str, float]:
    start = time.perf_counter()
    
    # Mock mode
    if settings.openrouter_api_key.startswith("sk-mock"):
        logger.info("Using MOCK AI response")
        time.sleep(1) # Simulate latency
        latency = time.perf_counter() - start
        
        # Simple heuristic to return valid JSON based on system prompt or role
        if "Parse Job Description" in system:
            return json.dumps({
                "title": "Mock Job Title",
                "must_have_skills": ["Python", "FastAPI"],
                "nice_to_have_skills": ["React"],
                "responsibilities": ["Build stuff"],
                "keywords": ["mock", "test"],
                "evidence": []
            }), latency
        elif "Match Analysis" in system:
            return json.dumps({
                "match_score": 85,
                "strong_matches": [{"item": "Python", "evidence_refs": []}],
                "missing_skills": [],
                "tailored_angle": "Focus on backend skills",
                "do_not_claim": [],
                "evidence": []
            }), latency
        elif "Tailor CV" in system:
             return json.dumps({
                "selected_projects": ["Project A"],
                "bullet_suggestions": [{"bullet": "Built X using Y", "evidence_refs": []}],
                "do_not_claim": [],
                "evidence": []
            }), latency
        return "{}", latency

    try:
        resp = _client().chat.completions.create(
            model=settings.openrouter_model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            response_format={"type": "json_object"}
        )
        latency = time.perf_counter() - start
        text = resp.choices[0].message.content or "{}"
        return text, round(latency, 3)
    except Exception as e:
        logger.error(f"AI Error: {e}")
        raise
