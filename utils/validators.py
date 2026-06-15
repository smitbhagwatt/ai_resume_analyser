"""
validators.py — Input validation helpers.

Catches bad inputs (empty text, too short, too long) before they
reach the LLM, saving API calls and giving users clear feedback.
"""

# Minimum number of words for a valid resume or JD
MIN_WORDS = 30

# Maximum characters to send to the LLM (prevents excessive token usage)
MAX_CHARS = 15000


def validate_resume(text: str) -> tuple[bool, str]:
    """
    Validate that the resume text is usable.

    Args:
        text: The resume text to validate.

    Returns:
        A tuple of (is_valid, error_message).
        If valid, error_message is an empty string.
    """
    if not text or not text.strip():
        return False, "Resume is empty. Please paste your resume or upload a PDF."

    word_count = len(text.split())

    if word_count < MIN_WORDS:
        return False, (
            f"Resume seems too short ({word_count} words). "
            f"A typical resume has at least {MIN_WORDS} words. "
            f"Please paste your full resume."
        )

    if len(text) > MAX_CHARS:
        return False, (
            f"Resume is too long ({len(text):,} characters). "
            f"Please keep it under {MAX_CHARS:,} characters."
        )

    return True, ""


def validate_job_description(text: str) -> tuple[bool, str]:
    """
    Validate that the job description text is usable.

    Args:
        text: The job description text to validate.

    Returns:
        A tuple of (is_valid, error_message).
        If valid, error_message is an empty string.
    """
    if not text or not text.strip():
        return False, "Job description is empty. Please paste the JD."

    word_count = len(text.split())

    if word_count < MIN_WORDS:
        return False, (
            f"Job description seems too short ({word_count} words). "
            f"Please paste the full job description for better results."
        )

    if len(text) > MAX_CHARS:
        return False, (
            f"Job description is too long ({len(text):,} characters). "
            f"Please keep it under {MAX_CHARS:,} characters."
        )

    return True, ""
