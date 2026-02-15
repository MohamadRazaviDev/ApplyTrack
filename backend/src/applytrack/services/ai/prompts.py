from applytrack.schemas.ai_schemas import ParsedJD, MatchResult, TailoredCVBullets

EVIDENCE_RULES = """
Rules:
- You MUST ONLY use evidence from the provided [JOB_DESCRIPTION_EVIDENCE] and [PROFILE_EVIDENCE] blocks.
- Every skill/responsibility claim MUST reference evidence ids in evidence_refs.
- If you cannot support something, write "Unknown" and add it to do_not_claim.
- Output MUST be valid JSON.
"""

def system_prompt(role: str) -> str:
    return f"You are an assistant helping with job applications. Role: {role}.\n{EVIDENCE_RULES}"

def build_parse_jd_prompt(jd_text: str) -> tuple[str, str]:
    system = system_prompt("Parse Job Description")
    system += f"\nReturn JSON matching schema: {ParsedJD.model_json_schema()}"
    user = f"Parse this job description:\n\n{jd_text}"
    return system, user

def build_match_prompt(jd_parsed: dict, profile_data: dict) -> tuple[str, str]:
    system = system_prompt("Match Analysis")
    system += f"\nReturn JSON matching schema: {MatchResult.model_json_schema()}"
    
    user = f"""
    [JOB_DESCRIPTION_EVIDENCE]
    {jd_parsed}
    
    [PROFILE_EVIDENCE]
    {profile_data}
    
    Analyze the match between the profile and the job description.
    """
    return system, user

def build_tailor_cv_prompt(jd_parsed: dict, profile_data: dict) -> tuple[str, str]:
    system = system_prompt("Tailor CV")
    system += f"\nReturn JSON matching schema: {TailoredCVBullets.model_json_schema()}"
    
    user = f"""
    [JOB_DESCRIPTION_EVIDENCE]
    {jd_parsed}
    
    [PROFILE_EVIDENCE]
    {profile_data}
    
    Suggest tailored bullets for the CV based on the job requirements.
    """
    return system, user
