from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

import pdfplumber
import docx
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# ------------------ DATABASE ------------------

DATABASE_URL = "postgresql://postgres:root@localhost/ai_career_copilot"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

# ------------------ APP ------------------

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

vectorizer = TfidfVectorizer(stop_words="english")

# ------------------ TEXT EXTRACTION ------------------

def extract_text_from_pdf(file):
    text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            if page.extract_text():
                text += page.extract_text() + " "
    return text.lower()

def extract_text_from_docx(file):
    document = docx.Document(file)
    return " ".join([para.text for para in document.paragraphs]).lower()

# ------------------ SKILL EXTRACTION ------------------

def extract_skills(text):
    return set(re.findall(r"\b[a-zA-Z]+\b", text.lower()))

# ------------------ RESUME ANALYSIS (IMPROVEMENT) ------------------

def analyze_resume_strength(resume_text):
    sections = {
        "skills": bool(re.search(r"\bskills?\b", resume_text)),
        "projects": bool(re.search(r"\bprojects?\b", resume_text)),
        "experience": bool(re.search(r"\bexperience|intern|worked\b", resume_text)),
    }

    action_verbs = re.findall(
        r"\b(designed|developed|implemented|optimized|led|created|improved)\b",
        resume_text
    )

    score = (
        (20 if sections["skills"] else 0) +
        (30 if sections["projects"] else 0) +
        (30 if sections["experience"] else 0) +
        min(len(action_verbs) * 2, 20)
    )

    return {
        "resume_score": score,
        "sections_found": sections,
        "action_verbs_count": len(action_verbs),
    }

# ------------------ JOB MATCHING ------------------

def match_jobs(resume_text):
    db = SessionLocal()
    rows = db.execute(
        text("SELECT id, title, company, description, required_skills FROM jobs")
    ).fetchall()
    db.close()

    if not rows:
        return []

    job_descriptions = [row.description for row in rows]
    job_descriptions.append(resume_text)

    tfidf = vectorizer.fit_transform(job_descriptions)
    similarities = cosine_similarity(tfidf[-1], tfidf[:-1]).flatten()

    resume_skills = extract_skills(resume_text)
    results = []

    for i, job in enumerate(rows):
        job_skills = set(
            skill.strip().lower()
            for skill in job.required_skills.split(",")
            if skill.strip()
        )

        matching_skills = resume_skills & job_skills
        missing_skills = job_skills - resume_skills

        skill_match_pct = (
            (len(matching_skills) / len(job_skills)) * 100 if job_skills else 0
        )

        similarity_pct = similarities[i] * 100
        final_score = (0.6 * similarity_pct) + (0.4 * skill_match_pct)

        results.append({
            "job_id": job.id,
            "title": job.title,
            "company": job.company,
            "similarity_score": round(similarity_pct, 2),
            "skill_match_percentage": round(skill_match_pct, 2),
            "matching_skills": list(matching_skills),
            "missing_skills": list(missing_skills),
            "final_score": round(final_score, 2),
        })

    results.sort(key=lambda x: x["final_score"], reverse=True)
    return results[:10]

# ------------------ API ------------------

@app.post("/upload_resume/")
async def upload_resume(file: UploadFile = File(...)):
    if file.filename.endswith(".pdf"):
        resume_text = extract_text_from_pdf(file.file)
    elif file.filename.endswith(".docx"):
        resume_text = extract_text_from_docx(file.file)
    else:
        return {"error": "Only PDF and DOCX allowed"}

    return {
        "resume_analysis": analyze_resume_strength(resume_text),
        "matched_jobs": match_jobs(resume_text),
    }