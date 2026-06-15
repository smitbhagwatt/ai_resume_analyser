# AI-Powered Resume & JD Matcher — Implementation Plan Review

**Author**: Smit Sachin Bhagwat · MIT-WPU · ECE-AIML · Batch 2023–2027

## Review of Your Existing Plan

Your plan is well-structured with 4 clear phases, a sensible tech stack, and good risk mitigation thinking. Below are my suggested changes grouped by category.

---

## ✅ What's Already Strong

- **Phase-gated approach** (Prompt → Core Logic → UI → Deploy) is correct — validating JSON output before building UI is smart
- **Risk table** with mitigations (retry logic, `json_repair`, `st.cache_data`) shows good foresight
- **Free deployment** via Streamlit Cloud is practical for a portfolio project
- **File structure** is clean and modular (`utils/parser.py`, `utils/llm.py`, `utils/prompt.py`)

---

## 🔧 Suggested Changes

### 1. Tech Stack — Consider Google Gemini Instead of Claude

> [!IMPORTANT]
> **Anthropic's Claude API is paid-only** (no free tier for API access). For a **free** project, consider using **Google Gemini API** which offers a generous free tier (15 RPM, 1M tokens/day on Gemini 2.0 Flash).

| Option | Free Tier | Best For |
|--------|-----------|----------|
| **Google Gemini** (Recommended) | ✅ Yes — 15 RPM free | Portfolio projects, zero cost |
| **Groq** (alternative) | ✅ Yes — fast inference | Speed-critical demos |
| Anthropic Claude | ❌ No free tier | Production apps with budget |
| OpenAI | ❌ No free tier | Production apps with budget |

> [!TIP]
> If you specifically want Claude for academic/learning reasons, that's fine — just budget ~$5 for API credits. But for "Free Deployment" as shown in your plan, Gemini is the better fit.

---

### 2. PDF Parsing — Add `pdfplumber` as Primary, PyPDF2 as Fallback

> [!NOTE]
> PyPDF2 is now **deprecated** in favor of `pypdf`. More importantly, `pdfplumber` handles complex resume layouts (tables, columns, styled text) much better.

```python
# Recommended approach in parser.py
try:
    import pdfplumber
    def extract_text(file) -> str:
        with pdfplumber.open(file) as pdf:
            return "\n".join(page.extract_text() or "" for page in pdf.pages)
except ImportError:
    from pypdf import PdfReader  # fallback
    def extract_text(file) -> str:
        reader = PdfReader(file)
        return "\n".join(page.extract_text() or "" for page in reader.pages)
```

---

### 3. Prompt Engineering — Add Structured Output Schema

Your plan says "tell the model to return ONLY valid JSON." A better approach is to define an explicit JSON schema in the prompt:

```python
# In prompt.py — add a clear output schema
OUTPUT_SCHEMA = {
    "match_score": "integer 0-100",
    "matching_keywords": ["list of matched skills/terms"],
    "missing_keywords": ["list of JD requirements not found in resume"],
    "rewritten_bullets": ["improved resume bullet points tailored to JD"],
    "cover_letter": "string — 3-paragraph tailored cover letter",
    "summary": "string — 2-3 sentence overall assessment"
}
```

> [!TIP]
> Adding a `"summary"` field gives users a quick TL;DR before reading details. This makes the UI much more engaging.

---

### 4. Phase 2 — Add Input Validation & Text Preprocessing

Your current Phase 2 jumps straight from parsing to LLM. Add a validation step:

```
Phase 2 (revised):
  ├── Resume parser (pdfplumber + plain text)
  ├── Input validation (min length, max tokens, language check)  ← NEW
  ├── Text preprocessing (clean whitespace, normalize encoding)  ← NEW
  ├── LLM caller
  └── Test in isolation
```

Why: Resumes with very little text (<50 words) or non-English content will produce garbage results. Catch these early.

---

### 5. Phase 3 — UI Enhancements

Your UI plan is solid. A few additions to make it **portfolio-worthy**:

| Your Plan | Suggested Addition |
|-----------|-------------------|
| `st.metric` for score | Add a **color-coded progress bar** (red < 40, yellow 40-70, green > 70) |
| Keywords as badges | Use **green badges** for matches, **red badges** for missing |
| Cover letter in `st.text_area` | Add a **"Copy to Clipboard"** button |
| — | Add a **"Download Report as PDF"** button |
| — | Add **session history** so users can compare multiple JDs |

---

### 6. Error Handling — Be More Specific

Your risk table mentions `try / except json.JSONDecodeError`. Expand this:

```python
# In llm.py — layered error handling
try:
    response = call_llm(resume, jd)
    result = json.loads(response)
except json.JSONDecodeError:
    # Attempt repair with json_repair library
    result = json_repair.loads(response)
except APIConnectionError:
    st.error("⚠️ Cannot reach the AI service. Please try again in a moment.")
except RateLimitError:
    st.error("⏳ Too many requests. Please wait 30 seconds.")
except Exception as e:
    st.error(f"Something went wrong: {str(e)}")
    logging.error(f"Unexpected error: {e}", exc_info=True)
```

---

### 7. Security — Add `.env` Handling Properly

> [!WARNING]
> Your plan mentions `.env` for API keys but doesn't mention **validation**. Always validate the key exists before making API calls.

```python
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("ANTHROPIC_API_KEY")  # or GOOGLE_API_KEY for Gemini

if not API_KEY:
    raise ValueError("API key not found. Create a .env file with your API key.")
```

---

### 8. Deployment — Add Streamlit Secrets Migration

When moving from local `.env` to Streamlit Cloud, you'll need to restructure how secrets are loaded:

```python
# config.py — works both locally and on Streamlit Cloud
import streamlit as st
import os

def get_api_key():
    # Try Streamlit secrets first (for cloud deployment)
    try:
        return st.secrets["API_KEY"]
    except (FileNotFoundError, KeyError):
        # Fall back to .env (for local development)
        from dotenv import load_dotenv
        load_dotenv()
        key = os.getenv("API_KEY")
        if not key:
            st.error("🔑 API key not configured. See README for setup instructions.")
            st.stop()
        return key
```

---

## 📁 Revised File Structure

```
resume-jd-matcher/
├── app.py                  ← Streamlit entry point
├── config.py               ← API key + settings management (NEW)
├── utils/
│   ├── __init__.py
│   ├── parser.py           ← PDF / text extraction (pdfplumber)
│   ├── llm.py              ← LLM API caller + JSON parsing
│   ├── prompt.py           ← System prompt + output schema
│   └── validators.py       ← Input validation helpers (NEW)
├── .env                    ← API key (git-ignored)
├── .gitignore
├── requirements.txt
└── README.md
```

---

## 📋 Revised Timeline

| Day | Phase | Tasks |
|-----|-------|-------|
| 1 | **Setup & Prompt** | Scaffolding, API key, design & test prompt with raw Python script |
| 2 | **Core Logic** | `parser.py` (pdfplumber), `validators.py`, `llm.py` with error handling |
| 3 | **Core Logic** | Integration testing, edge cases (short resumes, non-English, large PDFs) |
| 4-5 | **Streamlit UI** | Two-column layout, score display, badges, copy/download buttons |
| 6 | **Polish** | Loading states, error UX, mobile responsiveness, session history |
| 7 | **Deploy** | GitHub repo, Streamlit Cloud, README with demo link + screenshot |

---

## 🔑 Key Decision Needed From You

> [!IMPORTANT]
> **Which LLM provider do you want to use?**
> - **Google Gemini** (free, recommended for portfolio projects)
> - **Anthropic Claude** (paid, ~$5 minimum)
> - **Groq** (free tier, very fast)
> 
> This decision affects `requirements.txt`, `llm.py`, and deployment configuration.

---

## Verification Plan

### Automated Tests
- `python test_llm.py` — Validate JSON output schema against a sample resume + JD
- `python -m pytest tests/` — Unit tests for parser, validator, and LLM modules

### Manual Verification
- Test with 3+ real resumes in different formats (PDF, plain text)
- Test with job descriptions from different industries
- Verify Streamlit Cloud deployment loads correctly with secrets configured
- Check mobile responsiveness on phone browser
