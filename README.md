# ⚡ HireAI — Intelligent Recruitment & Resume Screening

HireAI is an AI-powered recruitment platform that automates resume screening using **Google Gemini**. Recruiters post a job, candidates' resumes are uploaded, and the AI reads each resume, scores it against the job's requirements, and surfaces the best matches — no manual reading needed.

## ✨ Features

- **AI Resume Screening** — Every uploaded PDF resume is parsed and scored against a job's required skills using Google Gemini.
- **Match Scoring** — Each candidate gets a 0–100 match score, a list of matched skills, and a list of skill gaps.
- **Auto-Select & Hiring Status** — Candidates crossing a configurable match-score threshold (default ≥80%) are automatically marked **Selected**. Once a job's required number of openings is filled with Selected candidates, the job is automatically marked **Hiring Done**.
- **Duplicate Protection** — The same candidate can't be screened twice for the same job. Duplicate detection works by matching either the candidate's email or the resume file itself, and shows the existing screening result (with date/time) instead of re-processing.
- **AI-Suggested Interview Questions & Resume Feedback** — For every candidate, Gemini generates tailored interview questions and resume improvement suggestions based on their specific gaps.
- **Job Management** — Create, edit, and delete job postings with auto-extracted required skills from a pasted job description.
- **Candidates Dashboard** — Filter by status (All / Selected / Shortlisted / Under Review / Rejected), search by name or email, and export the current view as CSV.
- **Authentication** — Simple email/password registration and login, with hashed passwords.

## 🛠️ Tech Stack

| Layer     | Technology |
|-----------|------------|
| Frontend  | HTML, CSS, JavaScript (vanilla, no framework) |
| Backend   | Python, Flask, Flask-CORS |
| Database  | MySQL |
| AI        | Google Gemini API (`google-generativeai`) |
| PDF Parsing | PyPDF2 |

## 📁 Project Structure

```
Hire-Ai-project/
├── Backend/
│   ├── app.py              # Flask API — auth, jobs, candidates, AI screening
│   ├── .env                # GEMINI_API_KEY (not committed)
│   └── venv/                # Python virtual environment (not committed)
└── Frontend/
    ├── index.html           # Landing page
    ├── login.html           # Login / Register
    ├── dashboard.html       # Overview dashboard
    ├── jobs.html            # Job postings — create/edit/delete
    ├── screening.html       # Upload & screen resumes for a job
    ├── candidates.html      # All candidates — filter, search, export
    ├── css/style.css
    └── js/
        ├── theme.js
        ├── sidebar.js
        └── dummy-data.js
```

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- MySQL Server (e.g. via XAMPP)
- A Google Gemini API key

### Backend Setup

```bash
cd Backend
python -m venv venv
venv\Scripts\activate          # Windows
pip install flask flask-cors mysql-connector-python python-dotenv google-generativeai PyPDF2 werkzeug
```

Create a `.env` file inside `Backend/`:
```
GEMINI_API_KEY=your_gemini_api_key_here
```

Create the MySQL database `hireai_db` with `users`, `jobs`, and `candidates` tables (see schema in `app.py`), then run:

```bash
python app.py
```

The API runs at `http://127.0.0.1:5000`.

### Frontend Setup

Open the `Frontend/` folder with a static server such as **VS Code Live Server**, then open `index.html`. The frontend calls the backend at `http://127.0.0.1:5000`, so make sure Flask is running first.

## 👥 Team

Built by a 3-member college team as part of a competitive/college project.

## 📄 License

This project is for educational purposes.
