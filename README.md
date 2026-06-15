# 🎯 AI Resume & JD Matcher

An AI-powered Streamlit web app that compares your resume against a job description and provides:

- **Match Score** (0-100) with a visual progress bar
- **Keyword Analysis** — matching vs missing skills/terms
- **Rewritten Bullet Points** — resume lines tailored to the JD
- **Tailored Cover Letter** — a ready-to-use 3-paragraph cover letter

Built with **Google Gemini 2.0 Flash** (free tier) for fast, structured AI analysis.

---

## 🖼️ Screenshots

> _Run the app and add screenshots here_

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10 or higher
- A free Google Gemini API key ([get one here](https://aistudio.google.com/apikey))

### Setup

```bash
# 1. Clone the repo
git clone https://github.com/YOUR_USERNAME/resume-jd-matcher.git
cd resume-jd-matcher

# 2. Create a virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Add your API key
copy .env.example .env
# Edit .env and replace 'your_api_key_here' with your actual key

# 5. Run the app
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`.

---

## 📁 Project Structure

```
resume-jd-matcher/
├── app.py                  ← Streamlit entry point (UI + app logic)
├── config.py               ← API key management (local + cloud)
├── utils/
│   ├── __init__.py
│   ├── parser.py           ← PDF text extraction (pdfplumber)
│   ├── llm.py              ← Gemini API caller + JSON parsing
│   ├── prompt.py           ← System prompt + output schema
│   └── validators.py       ← Input validation helpers
├── .env                    ← Your API key (git-ignored)
├── .env.example            ← Template for .env
├── .gitignore
├── requirements.txt
└── README.md
```

---

## 🛠️ Tech Stack

| Technology | Purpose |
|------------|---------|
| Python 3.10+ | Core language |
| Streamlit | Web UI framework |
| Google Gemini API | LLM for resume analysis |
| pdfplumber | PDF text extraction |
| python-dotenv | Environment variable management |

---

## ☁️ Deploy on Streamlit Cloud

1. Push your code to a GitHub repository
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub repo and select `app.py`
4. Add your API key in **Settings → Secrets**:
   ```toml
   GOOGLE_API_KEY = "your_key_here"
   ```
5. Click **Deploy**

---

## 📝 How It Works

1. **Input**: User pastes their resume (or uploads a PDF) and a job description
2. **Parse**: `pdfplumber` extracts text from uploaded PDFs
3. **Validate**: Input validators check for minimum length and content quality
4. **Analyze**: The resume + JD are sent to Google Gemini with a structured prompt
5. **Display**: Results are rendered with match score, keyword badges, bullet rewrites, and a cover letter

---

## 👤 Author

**Smit Sachin Bhagwat**
MIT-WPU · ECE-AIML · Batch 2023–2027

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).
