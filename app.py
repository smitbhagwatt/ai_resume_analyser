"""
app.py — Main Streamlit application for the AI Resume & JD Matcher.

This is the entry point. Run with: streamlit run app.py

The app provides a two-column layout where users can input their resume
(via text paste or PDF upload) and a job description, then get an
AI-powered analysis with match score, keyword comparison, rewritten
bullet points, and a tailored cover letter.
"""

import streamlit as st
from config import get_api_key
from utils.parser import extract_text_from_pdf
from utils.validators import validate_resume, validate_job_description
from utils.llm import analyze_resume


# ──────────────────────────────────────────────
# Page Configuration
# ──────────────────────────────────────────────

st.set_page_config(
    page_title="AI Resume & JD Matcher",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ──────────────────────────────────────────────
# Custom CSS for a polished, modern look
# ──────────────────────────────────────────────

st.markdown("""
<style>
    /* ── Google Font ── */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    * { font-family: 'Inter', sans-serif; }

    /* ── Main container ── */
    .main .block-container {
        padding-top: 2rem;
        max-width: 1200px;
    }

    /* ── Header gradient ── */
    .app-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem 2.5rem;
        border-radius: 16px;
        margin-bottom: 2rem;
        color: white;
        text-align: center;
    }
    .app-header h1 {
        margin: 0;
        font-size: 2.2rem;
        font-weight: 700;
        letter-spacing: -0.5px;
    }
    .app-header p {
        margin: 0.5rem 0 0 0;
        font-size: 1.05rem;
        opacity: 0.9;
    }

    /* ── Score card ── */
    .score-card {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        border-radius: 16px;
        padding: 2rem;
        text-align: center;
        margin-bottom: 1.5rem;
        border: 1px solid rgba(255,255,255,0.08);
    }
    .score-value {
        font-size: 4rem;
        font-weight: 700;
        line-height: 1;
        margin: 0.5rem 0;
    }
    .score-label {
        font-size: 0.95rem;
        color: #a0a0b0;
        text-transform: uppercase;
        letter-spacing: 1.5px;
    }

    /* ── Score progress bar ── */
    .score-bar-bg {
        width: 100%;
        height: 10px;
        background: rgba(255,255,255,0.1);
        border-radius: 5px;
        margin-top: 1rem;
        overflow: hidden;
    }
    .score-bar-fill {
        height: 100%;
        border-radius: 5px;
        transition: width 0.8s ease;
    }

    /* ── Keyword badges ── */
    .keyword-badge {
        display: inline-block;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 500;
        margin: 4px;
    }
    .badge-match {
        background: rgba(46, 213, 115, 0.15);
        color: #2ed573;
        border: 1px solid rgba(46, 213, 115, 0.3);
    }
    .badge-missing {
        background: rgba(255, 71, 87, 0.15);
        color: #ff4757;
        border: 1px solid rgba(255, 71, 87, 0.3);
    }

    /* ── Section cards ── */
    .section-card {
        background: rgba(255,255,255,0.03);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1rem;
    }
    .section-title {
        font-size: 1.1rem;
        font-weight: 600;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 8px;
    }

    /* ── Bullet point cards ── */
    .bullet-card {
        background: rgba(102, 126, 234, 0.08);
        border-left: 3px solid #667eea;
        padding: 12px 16px;
        border-radius: 0 8px 8px 0;
        margin-bottom: 8px;
        font-size: 0.93rem;
        line-height: 1.5;
    }

    /* ── Analyze button ── */
    div.stButton > button {
        width: 100%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.8rem 2rem;
        font-size: 1.1rem;
        font-weight: 600;
        border-radius: 12px;
        letter-spacing: 0.3px;
        transition: all 0.3s ease;
    }
    div.stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
    }

    /* ── Text area styling ── */
    .stTextArea textarea {
        border-radius: 10px;
        border: 1px solid rgba(255,255,255,0.12);
        font-size: 0.9rem;
    }

    /* ── Hide Streamlit branding ── */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)


# ──────────────────────────────────────────────
# Header
# ──────────────────────────────────────────────

st.markdown("""
<div class="app-header">
    <h1>🎯 AI Resume & JD Matcher</h1>
    <p>Paste your resume and a job description to get an AI-powered match analysis</p>
</div>
""", unsafe_allow_html=True)


# ──────────────────────────────────────────────
# Input Section — Two Column Layout
# ──────────────────────────────────────────────

col_resume, col_jd = st.columns(2, gap="large")

with col_resume:
    st.markdown("### 📄 Your Resume")

    # PDF upload option
    uploaded_pdf = st.file_uploader(
        "Upload PDF",
        type=["pdf"],
        help="Upload your resume as a PDF file",
        key="pdf_uploader",
    )

    # Text paste option
    resume_text = st.text_area(
        "Or paste your resume text",
        height=300,
        placeholder="Paste your resume content here...",
        key="resume_input",
    )

    # If PDF was uploaded, extract text from it
    if uploaded_pdf is not None:
        try:
            resume_text = extract_text_from_pdf(uploaded_pdf)
            st.success(f"✅ Extracted {len(resume_text.split())} words from PDF")
        except ValueError as e:
            st.error(str(e))
            resume_text = ""


with col_jd:
    st.markdown("### 💼 Job Description")

    jd_text = st.text_area(
        "Paste the job description",
        height=350,
        placeholder="Paste the full job description here...",
        key="jd_input",
    )


# ──────────────────────────────────────────────
# Analyze Button
# ──────────────────────────────────────────────

st.markdown("")  # spacing

if st.button("🚀 Analyze Match", key="analyze_btn"):

    # Step 1: Validate inputs
    resume_ok, resume_err = validate_resume(resume_text)
    jd_ok, jd_err = validate_job_description(jd_text)

    if not resume_ok:
        st.error(resume_err)
    elif not jd_ok:
        st.error(jd_err)
    else:
        # Step 2: Get the API key
        api_key = get_api_key()

        # Step 3: Call the LLM with a loading spinner
        with st.spinner("🔍 Analyzing your resume against the job description..."):
            try:
                result = analyze_resume(resume_text, jd_text, api_key)
            except ValueError as e:
                st.error(f"⚠️ {e}")
                st.stop()
            except Exception as e:
                st.error(
                    f"⚠️ Something went wrong: {str(e)}\n\n"
                    "Please check your API key and try again."
                )
                st.stop()

        # Step 4: Store result in session state for display
        st.session_state["result"] = result


# ──────────────────────────────────────────────
# Results Display
# ──────────────────────────────────────────────

if "result" in st.session_state:
    result = st.session_state["result"]

    st.markdown("---")
    st.markdown("## 📊 Analysis Results")

    # ── Score Card ──
    score = result["match_score"]

    # Determine score color
    if score >= 70:
        score_color = "#2ed573"  # green
        score_label = "Strong Match"
    elif score >= 40:
        score_color = "#ffa502"  # orange
        score_label = "Moderate Match"
    else:
        score_color = "#ff4757"  # red
        score_label = "Needs Improvement"

    st.markdown(f"""
    <div class="score-card">
        <div class="score-label">MATCH SCORE</div>
        <div class="score-value" style="color: {score_color};">{score}%</div>
        <div class="score-label">{score_label}</div>
        <div class="score-bar-bg">
            <div class="score-bar-fill" style="width: {score}%; background: {score_color};"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Summary ──
    st.info(f"💡 **Summary:** {result['summary']}")

    # ── Keywords Section ──
    col_match, col_miss = st.columns(2)

    with col_match:
        st.markdown("""
        <div class="section-card">
            <div class="section-title">✅ Matching Keywords</div>
        """, unsafe_allow_html=True)

        match_badges = ""
        for kw in result["matching_keywords"]:
            match_badges += f'<span class="keyword-badge badge-match">{kw}</span>'
        if not result["matching_keywords"]:
            match_badges = '<span style="color:#a0a0b0;">No matches found</span>'

        st.markdown(match_badges + "</div>", unsafe_allow_html=True)

    with col_miss:
        st.markdown("""
        <div class="section-card">
            <div class="section-title">❌ Missing Keywords</div>
        """, unsafe_allow_html=True)

        miss_badges = ""
        for kw in result["missing_keywords"]:
            miss_badges += f'<span class="keyword-badge badge-missing">{kw}</span>'
        if not result["missing_keywords"]:
            miss_badges = '<span style="color:#a0a0b0;">None — great coverage!</span>'

        st.markdown(miss_badges + "</div>", unsafe_allow_html=True)

    # ── Rewritten Bullets ──
    st.markdown("")
    with st.expander("✍️ **Rewritten Resume Bullet Points** — Click to expand", expanded=True):
        for i, bullet in enumerate(result["rewritten_bullets"], 1):
            st.markdown(
                f'<div class="bullet-card">• {bullet}</div>',
                unsafe_allow_html=True,
            )

    # ── Cover Letter ──
    st.markdown("")
    with st.expander("📝 **Tailored Cover Letter** — Click to expand"):
        st.markdown(result["cover_letter"])
        st.markdown("")
        # Copy button using Streamlit's built-in code block
        st.code(result["cover_letter"], language=None)
        st.caption("👆 Click the copy icon in the top-right of the box above to copy")
