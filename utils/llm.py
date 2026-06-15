"""
llm.py — Handles communication with the Google Gemini API.

Sends the resume + JD to Gemini and parses the structured JSON response.
Uses gemini-2.0-flash for fast, free-tier-friendly inference.
"""

import json
import re
import google.generativeai as genai
from utils.prompt import build_prompt


def analyze_resume(resume_text: str, jd_text: str, api_key: str) -> dict:
    """
    Send resume and JD to Gemini and get a structured analysis.

    Args:
        resume_text: The extracted resume text.
        jd_text: The job description text.
        api_key: Google Gemini API key.

    Returns:
        A dictionary with keys: match_score, summary, matching_keywords,
        missing_keywords, rewritten_bullets, cover_letter.

    Raises:
        ValueError: If the API response cannot be parsed as valid JSON.
        Exception: If the API call itself fails.
    """
    # Configure the Gemini API with the user's key
    genai.configure(api_key=api_key)

    # Use Gemini 3.5 Flash since it is available on this API key
    model = genai.GenerativeModel("gemini-3.5-flash")

    # Build the prompt with resume and JD
    prompt = build_prompt(resume_text, jd_text)

    # Call the API
    response = model.generate_content(prompt)

    # Extract the text from the response
    raw_text = response.text

    # Parse the JSON response
    result = _parse_json_response(raw_text)

    # Validate that all expected keys are present
    _validate_response(result)

    return result


def _parse_json_response(raw_text: str) -> dict:
    """
    Parse JSON from the LLM response, handling common formatting issues.

    The model sometimes wraps JSON in markdown code blocks (```json ... ```),
    so we strip those if present before parsing.

    Args:
        raw_text: Raw text response from the LLM.

    Returns:
        Parsed dictionary.

    Raises:
        ValueError: If the response cannot be parsed as JSON.
    """
    text = raw_text.strip()

    # Remove markdown code block wrappers if present (```json ... ```)
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*\n?", "", text)
        text = re.sub(r"\n?```\s*$", "", text)

    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        raise ValueError(
            f"The AI returned an invalid response. Please try again.\n"
            f"Parse error: {e}"
        )


def _validate_response(result: dict) -> None:
    """
    Ensure the parsed response contains all required keys.

    If any key is missing, we add a sensible default so the UI
    doesn't crash. This is more resilient than raising an error.

    Args:
        result: The parsed JSON dictionary from the LLM.
    """
    defaults = {
        "match_score": 0,
        "summary": "Analysis could not generate a summary.",
        "matching_keywords": [],
        "missing_keywords": [],
        "rewritten_bullets": [],
        "cover_letter": "Cover letter could not be generated.",
    }

    for key, default_value in defaults.items():
        if key not in result:
            result[key] = default_value

    # Clamp match_score to 0-100 range
    score = result["match_score"]
    if isinstance(score, (int, float)):
        result["match_score"] = max(0, min(100, int(score)))
    else:
        result["match_score"] = 0
