"""
prompt.py — Contains the system prompt and output schema for the LLM.

The prompt instructs the Gemini model to act as an expert recruiter and
return a structured JSON response comparing a resume against a job description.
"""


# The JSON schema we expect the LLM to return.
# This is included in the prompt so the model knows exactly what to output.
OUTPUT_SCHEMA = {
    "match_score": "integer 0-100",
    "summary": "2-3 sentence overall assessment",
    "matching_keywords": ["skills/terms found in both resume and JD"],
    "missing_keywords": ["JD requirements not found in resume"],
    "rewritten_bullets": ["improved resume bullet points tailored to this JD"],
    "cover_letter": "3-paragraph tailored cover letter",
}


def build_prompt(resume_text: str, jd_text: str) -> str:
    """
    Build the full prompt that gets sent to Gemini.

    Args:
        resume_text: Extracted text from the user's resume.
        jd_text: The job description text.

    Returns:
        A formatted prompt string with the system instruction,
        resume, job description, and expected output format.
    """
    prompt = f"""You are an expert career coach and technical recruiter with 15 years of experience.

Your task: Analyze the RESUME against the JOB DESCRIPTION and return a structured JSON evaluation.

INSTRUCTIONS:
1. Calculate a match score (0-100) based on skills, experience, and qualifications overlap.
2. Identify keywords/skills that match between resume and JD.
3. Identify important JD requirements missing from the resume.
4. Rewrite 3-5 resume bullet points to better align with the JD (use action verbs, quantify results).
5. Draft a concise 3-paragraph cover letter tailored to the role.
6. Provide a brief 2-3 sentence overall assessment.

RESUME:
\"\"\"
{resume_text}
\"\"\"

JOB DESCRIPTION:
\"\"\"
{jd_text}
\"\"\"

Respond with ONLY valid JSON in this exact format (no markdown, no extra text):
{{
    "match_score": <integer 0-100>,
    "summary": "<2-3 sentence overall assessment>",
    "matching_keywords": ["keyword1", "keyword2", ...],
    "missing_keywords": ["keyword1", "keyword2", ...],
    "rewritten_bullets": ["bullet1", "bullet2", ...],
    "cover_letter": "<3-paragraph cover letter>"
}}
"""
    return prompt
