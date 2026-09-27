import os
import io
import json
import re
import hashlib
from dotenv import load_dotenv
import google.generativeai as genai
import PyPDF2
from flask import Flask, jsonify, request
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
gemini_model = genai.GenerativeModel('gemini-3.6-flash')

app = Flask(__name__)
CORS(app)

# Threshold above which a screened candidate is automatically marked "Selected"
AUTO_SELECT_THRESHOLD = 80

# ---------- Database connection ----------
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",  # default XAMPP MySQL password is empty; change if you set one
        database="hireai_db"
    )

@app.route('/')
def home():
    return jsonify({"message": "HireAI backend is running!"})

# ---------- Register ----------
@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    hashed_password = generate_password_hash(password)

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (name, email, password) VALUES (%s, %s, %s)",
            (name, email, hashed_password)
        )
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"message": "Registered successfully"}), 201
    except mysql.connector.errors.IntegrityError:
        return jsonify({"error": "Email already registered"}), 409
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ---------- Login ----------
@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user and check_password_hash(user['password'], password):
            return jsonify({
                "message": "Login successful",
                "user": {"name": user['name'], "email": user['email']}
            }), 200
        else:
            return jsonify({"error": "Invalid email or password"}), 401
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ---------- Get all jobs ----------
@app.route('/api/jobs', methods=['GET'])
def get_jobs():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT j.*,
                (SELECT COUNT(*) FROM candidates c
                 WHERE c.job_id = j.id AND c.status = 'Selected') AS selected_count
            FROM jobs j
            ORDER BY j.id DESC
        """)
        jobs = cursor.fetchall()
        cursor.close()
        conn.close()

        for job in jobs:
            job['skills'] = job['skills'].split(',') if job['skills'] else []
            job['postedOn'] = str(job['posted_on'])
            job['candidatesScreened'] = job['candidates_screened']
            job['openingsRequired'] = job.get('openings_required', 1)
            job['selectedCount'] = job.pop('selected_count', 0)
            del job['posted_on']
            del job['candidates_screened']
            if 'openings_required' in job:
                del job['openings_required']

        return jsonify(jobs), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ---------- Create a new job ----------
@app.route('/api/jobs', methods=['POST'])
def create_job():
    data = request.get_json()
    title = data.get('title')
    department = data.get('department')
    skills = data.get('skills', [])
    openings_required = data.get('openingsRequired', 1)

    if not title or not department:
        return jsonify({"error": "Title and department are required"}), 400

    try:
        openings_required = int(openings_required)
        if openings_required < 1:
            openings_required = 1
    except (TypeError, ValueError):
        openings_required = 1

    skills_str = ','.join(skills) if skills else ''

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO jobs (title, department, status, skills, openings_required) VALUES (%s, %s, %s, %s, %s)",
            (title, department, 'Active', skills_str, openings_required)
        )
        conn.commit()
        new_id = cursor.lastrowid
        cursor.close()
        conn.close()
        return jsonify({"message": "Job created", "id": new_id}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ---------- Update a job ----------
@app.route('/api/jobs/<int:job_id>', methods=['PUT'])
def update_job(job_id):
    data = request.get_json()
    title = data.get('title')
    department = data.get('department')
    status = data.get('status')
    skills = data.get('skills', [])
    openings_required = data.get('openingsRequired')

    if not title or not department:
        return jsonify({"error": "Title and department are required"}), 400

    skills_str = ','.join(skills) if skills else ''

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        if openings_required is not None:
            try:
                openings_required = max(1, int(openings_required))
            except (TypeError, ValueError):
                openings_required = 1
            cursor.execute(
                "UPDATE jobs SET title=%s, department=%s, status=%s, skills=%s, openings_required=%s WHERE id=%s",
                (title, department, status or 'Active', skills_str, openings_required, job_id)
            )
        else:
            cursor.execute(
                "UPDATE jobs SET title=%s, department=%s, status=%s, skills=%s WHERE id=%s",
                (title, department, status or 'Active', skills_str, job_id)
            )
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"message": "Job updated"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ---------- Delete a job ----------
@app.route('/api/jobs/<int:job_id>', methods=['DELETE'])
def delete_job(job_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        # Remove candidates linked to this job first (foreign key constraint)
        cursor.execute("DELETE FROM candidates WHERE job_id = %s", (job_id,))
        cursor.execute("DELETE FROM jobs WHERE id = %s", (job_id,))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"message": "Job deleted"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ---------- Get all candidates (optionally filter by job_id) ----------
@app.route('/api/candidates', methods=['GET'])
def get_candidates():
    job_id = request.args.get('jobId')
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        if job_id:
            cursor.execute("SELECT * FROM candidates WHERE job_id = %s ORDER BY match_score DESC", (job_id,))
        else:
            cursor.execute("SELECT * FROM candidates ORDER BY match_score DESC")
        candidates = cursor.fetchall()
        cursor.close()
        conn.close()

        for c in candidates:
            c['jobId'] = c.pop('job_id')
            c['matchScore'] = c.pop('match_score')
            c['skillsMatched'] = c.pop('skills_matched').split(',') if c['skills_matched'] else []
            c['skillsMissing'] = c.pop('skills_missing').split(',') if c['skills_missing'] else []
            iq = c.pop('interview_questions', None)
            rs = c.pop('resume_suggestions', None)
            c['interviewQuestions'] = json.loads(iq) if iq else []
            c['resumeSuggestions'] = json.loads(rs) if rs else []
            screened_at = c.pop('screened_at', None)
            c['screenedAt'] = str(screened_at) if screened_at else None
            c.pop('resume_hash', None)

        return jsonify(candidates), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ---------- Update a candidate's status ----------
@app.route('/api/candidates/<int:candidate_id>/status', methods=['PATCH'])
def update_candidate_status(candidate_id):
    data = request.get_json()
    new_status = data.get('status')

    if not new_status:
        return jsonify({"error": "Status is required"}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT job_id FROM candidates WHERE id = %s", (candidate_id,))
        row = cursor.fetchone()
        if not row:
            cursor.close()
            conn.close()
            return jsonify({"error": "Candidate not found"}), 404

        cursor2 = conn.cursor()
        cursor2.execute("UPDATE candidates SET status = %s WHERE id = %s", (new_status, candidate_id))
        conn.commit()
        cursor2.close()

        update_job_hiring_status(conn, row['job_id'])

        cursor.close()
        conn.close()
        return jsonify({"message": "Status updated"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ---------- Dashboard summary ----------
@app.route('/api/dashboard', methods=['GET'])
def get_dashboard():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT COUNT(*) as total FROM jobs WHERE status='Active'")
        total_jobs = cursor.fetchone()['total']

        cursor.execute("SELECT COUNT(*) as total FROM candidates")
        total_candidates = cursor.fetchone()['total']

        cursor.execute("SELECT COUNT(*) as total FROM candidates WHERE status='Shortlisted'")
        shortlisted = cursor.fetchone()['total']

        cursor.execute("SELECT AVG(match_score) as avg_score FROM candidates")
        avg_result = cursor.fetchone()
        avg_score = round(avg_result['avg_score']) if avg_result['avg_score'] else 0

        cursor.execute("SELECT id, title, department, posted_on, status FROM jobs ORDER BY id DESC LIMIT 3")
        recent_jobs = cursor.fetchall()
        for job in recent_jobs:
            job['postedOn'] = str(job['posted_on'])
            del job['posted_on']

        cursor.execute("SELECT id, name, experience, match_score FROM candidates ORDER BY match_score DESC LIMIT 4")
        top_candidates = cursor.fetchall()
        for c in top_candidates:
            c['matchScore'] = c.pop('match_score')

        cursor.close()
        conn.close()

        return jsonify({
            "stats": {
                "totalJobs": total_jobs,
                "totalCandidates": total_candidates,
                "shortlisted": shortlisted,
                "avgMatchScore": avg_score
            },
            "recentJobs": recent_jobs,
            "topCandidates": top_candidates
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ---------- Extract text from uploaded PDF ----------
def extract_pdf_text(file_stream):
    reader = PyPDF2.PdfReader(file_stream)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text

# ---------- Recompute a job's hiring status based on how many candidates are Selected ----------
def update_job_hiring_status(conn, job_id):
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT openings_required, status FROM jobs WHERE id = %s", (job_id,))
    job = cursor.fetchone()
    if not job:
        cursor.close()
        return

    openings_required = job.get('openings_required') or 1
    cursor.execute(
        "SELECT COUNT(*) as cnt FROM candidates WHERE job_id = %s AND status = 'Selected'",
        (job_id,)
    )
    selected_count = cursor.fetchone()['cnt']
    cursor.close()

    cursor2 = conn.cursor()
    if selected_count >= openings_required:
        cursor2.execute("UPDATE jobs SET status = %s WHERE id = %s", ('Hiring Done', job_id))
    elif job.get('status') == 'Hiring Done':
        # openings requirement no longer met (e.g. a Selected candidate was un-selected) - reopen the job
        cursor2.execute("UPDATE jobs SET status = %s WHERE id = %s", ('Active', job_id))
    conn.commit()
    cursor2.close()

# ---------- Real AI-powered resume screening ----------
@app.route('/api/screen-resume', methods=['POST'])
def screen_resume():
    job_id = request.form.get('jobId')
    file = request.files.get('resume')

    if not job_id or not file:
        return jsonify({"error": "jobId and resume file are required"}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM jobs WHERE id = %s", (job_id,))
        job = cursor.fetchone()
        if not job:
            cursor.close()
            conn.close()
            return jsonify({"error": "Job not found"}), 404

        file_bytes = file.read()
        if not file_bytes:
            cursor.close()
            conn.close()
            return jsonify({"error": "Empty file uploaded"}), 400

        resume_hash = hashlib.sha256(file_bytes).hexdigest()
        resume_text = extract_pdf_text(io.BytesIO(file_bytes))
        if not resume_text.strip():
            cursor.close()
            conn.close()
            return jsonify({"error": "Could not read text from this PDF. Try a different file."}), 400

        # Cheap email extraction (no AI call) so we can duplicate-check before spending a Gemini call
        email_match = re.search(r'[\w\.\-]+@[\w\.\-]+\.\w+', resume_text)
        extracted_email = email_match.group(0).lower() if email_match else None

        # ---------- Duplicate check: same job + (same resume file OR same email) ----------
        if extracted_email:
            cursor.execute(
                "SELECT * FROM candidates WHERE job_id = %s AND (resume_hash = %s OR LOWER(email) = %s) "
                "ORDER BY id DESC LIMIT 1",
                (job_id, resume_hash, extracted_email)
            )
        else:
            cursor.execute(
                "SELECT * FROM candidates WHERE job_id = %s AND resume_hash = %s ORDER BY id DESC LIMIT 1",
                (job_id, resume_hash)
            )
        existing = cursor.fetchone()

        if existing:
            cursor.close()
            conn.close()
            return jsonify({
                "duplicate": True,
                "message": "This candidate has already been screened for this job.",
                "id": existing['id'],
                "jobId": existing['job_id'],
                "name": existing['name'],
                "email": existing['email'],
                "matchScore": existing['match_score'],
                "status": existing['status'],
                "screenedAt": str(existing['screened_at']) if existing.get('screened_at') else None
            }), 200

        prompt = f"""
You are a recruitment AI. Compare this candidate's resume against the job requirements.

JOB TITLE: {job['title']}
REQUIRED SKILLS: {job['skills']}

RESUME TEXT:
{resume_text[:6000]}

Respond with ONLY valid JSON (no markdown, no explanation) in this exact format:
{{
  "name": "candidate's full name extracted from resume",
  "email": "candidate's email extracted from resume, or empty string if not found",
  "experience": "e.g. '3 years' or 'Fresher'",
  "matchScore": 0-100 integer,
  "skillsMatched": ["skill1", "skill2"],
  "skillsMissing": ["skill3"],
  "status": "Shortlisted if matchScore>=75, Under Review if 40-74, Rejected if <40",
  "interviewQuestions": ["4 specific interview questions tailored to this candidate's resume and the missing/weak areas"],
  "resumeSuggestions": ["3 specific, actionable suggestions to improve this exact resume for this exact job"]
}}
"""
        response = gemini_model.generate_content(prompt)
        raw_text = response.text.strip()
        raw_text = re.sub(r"^```json\s*|\s*```$", "", raw_text, flags=re.MULTILINE).strip()
        result = json.loads(raw_text)

        match_score = result.get('matchScore', 0)
        # Auto-select overrides the AI's own suggested status once the threshold is crossed
        final_status = 'Selected' if match_score >= AUTO_SELECT_THRESHOLD else result.get('status', 'Under Review')
        final_email = result.get('email') or extracted_email or ''

        cursor2 = conn.cursor()
        cursor2.execute(
            "INSERT INTO candidates "
            "(job_id, name, email, match_score, skills_matched, skills_missing, experience, status, "
            "interview_questions, resume_suggestions, resume_hash, screened_at) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())",
            (
                job_id, result.get('name', 'Unknown'), final_email,
                match_score,
                ','.join(result.get('skillsMatched', [])),
                ','.join(result.get('skillsMissing', [])),
                result.get('experience', 'N/A'),
                final_status,
                json.dumps(result.get('interviewQuestions', [])),
                json.dumps(result.get('resumeSuggestions', [])),
                resume_hash
            )
        )
        conn.commit()
        new_id = cursor2.lastrowid
        cursor2.close()

        cursor.execute("SELECT screened_at FROM candidates WHERE id = %s", (new_id,))
        screened_row = cursor.fetchone()

        update_job_hiring_status(conn, job_id)

        cursor.close()
        conn.close()

        result['id'] = new_id
        result['jobId'] = int(job_id)
        result['status'] = final_status
        result['email'] = final_email
        result['duplicate'] = False
        result['screenedAt'] = str(screened_row['screened_at']) if screened_row else None
        return jsonify(result), 200

    except json.JSONDecodeError:
        return jsonify({"error": "AI response could not be parsed. Try again."}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)