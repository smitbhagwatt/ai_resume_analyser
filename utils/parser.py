"""
parser.py — Extracts text from uploaded PDF files or plain text input.

Uses pdfplumber as the primary PDF parser because it handles complex
resume layouts (tables, columns, styled text) better than alternatives.
"""

import pdfplumber


def extract_text_from_pdf(uploaded_file) -> str:
    """
    Extract all text content from an uploaded PDF file.

    Args:
        uploaded_file: A Streamlit UploadedFile object (or any file-like object).

    Returns:
        A single string with all text from all pages, separated by newlines.

    Raises:
        ValueError: If no text could be extracted from the PDF.
    """
    text_parts = []

    with pdfplumber.open(uploaded_file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)

    full_text = "\n".join(text_parts)

    if not full_text.strip():
        raise ValueError(
            "Could not extract any text from the PDF. "
            "The file might be scanned/image-based. "
            "Please paste your resume text instead."
        )

    return full_text
