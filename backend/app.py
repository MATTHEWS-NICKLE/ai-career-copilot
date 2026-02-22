from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import pdfplumber
import docx
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

DATABASE_URL = "postgresql://postgres:root@localhost/ai_career_copilot"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

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
    # simple skill extraction (based on words)
    words = re.findall(r'\b\w+\b', text.lower())
    return set(words)

# ------------------ JOB MATCHING ------------------

def match_jobs(resume_text):
    db = SessionLocal()
    result = db.execute(
        text("SELECT id, title, company, description, required_skills FROM jobs")
    )
    jobs = result.fetchall()
    db.close()

    job_descriptions = [job.description for job in jobs]
    job_descriptions.append(resume_text)

    tfidf_matrix = vectorizer.fit_transform(job_descriptions)
    similarity_scores = cosine_similarity(
        tfidf_matrix[-1], tfidf_matrix[:-1]
    ).flatten()

    resume_skills = extract_skills(resume_text)

    results = []

    for i, job in enumerate(jobs):
        required_skills = set(
            skill.strip().lower() for skill in job.required_skills.split(",")
        )

        matching_skills = resume_skills.intersection(required_skills)
        missing_skills = required_skills - resume_skills

        if len(required_skills) > 0:
            skill_match_percentage = (len(matching_skills) / len(required_skills)) * 100
        else:
            skill_match_percentage = 0

        similarity_percentage = similarity_scores[i] * 100

        # Final Weighted Score
        final_score = (0.6 * similarity_percentage) + (0.4 * skill_match_percentage)

        results.append({
            "job_id": job.id,
            "title": job.title,
            "company": job.company,
            "similarity_score": round(similarity_percentage, 2),
            "skill_match_percentage": round(skill_match_percentage, 2),
            "missing_skills": list(missing_skills),
            "final_score": round(final_score, 2)
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

    matched_jobs = match_jobs(resume_text)

    return {"matched_jobs": matched_jobs}