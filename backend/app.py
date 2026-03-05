from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.orm import sessionmaker, declarative_base, Session
import pdfplumber
import docx
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import os

# configuration (supports environment variable override)
DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://postgres:root@localhost/ai_career_copilot"
)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

app = FastAPI(title="AI Career Copilot API")

# ---------- CORS MIDDLEWARE ----------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- MODELS & SCHEMAS ----------

class JobModel(Base):
    __tablename__ = "jobs"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    company = Column(String)
    description = Column(Text)
    required_skills = Column(String)


class JobBase(BaseModel):
    title: str
    company: str
    description: str
    required_skills: str


class JobCreate(JobBase):
    pass


class Job(JobBase):
    id: int

    class Config:
        orm_mode = True


# make sure tables exist
Base.metadata.create_all(bind=engine)


# dependency for database session

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ---------- GLOBAL CACHE ----------
vectorizer = TfidfVectorizer(stop_words="english")
job_cache = {"jobs": [], "tfidf_matrix": None}


def refresh_job_cache():
    """Loads jobs from the database and computes a TF-IDF matrix of descriptions."""
    db: Session = SessionLocal()
    try:
        jobs = db.query(JobModel).all()
        job_cache["jobs"] = jobs
        descriptions = [job.description for job in jobs]
        if descriptions:
            job_cache["tfidf_matrix"] = vectorizer.fit_transform(descriptions)
        else:
            job_cache["tfidf_matrix"] = None
    finally:
        db.close()


# initialize cache once
refresh_job_cache()


# ---------- TEXT EXTRACTION UTILITIES ----------

def extract_text_from_pdf(file):
    text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + " "
    return text.lower()


def extract_text_from_docx(file):
    document = docx.Document(file)
    return " ".join([para.text for para in document.paragraphs]).lower()


# ---------- SKILL EXTRACTION ----------

def extract_skills(text: str) -> set:
    words = re.findall(r"\b\w+\b", text.lower())
    return set(words)


# ---------- MATCHING LOGIC ----------

def match_jobs(resume_text: str) -> List[dict]:
    """Return top-10 jobs ranked by a weighted combination of description similarity
    and explicit skill matching."""

    jobs = job_cache.get("jobs", [])
    tfidf_matrix = job_cache.get("tfidf_matrix")

    if tfidf_matrix is None or len(jobs) == 0:
        return []

    resume_vector = vectorizer.transform([resume_text])
    similarity_scores = cosine_similarity(resume_vector, tfidf_matrix).flatten()

    resume_skills = extract_skills(resume_text)

    results = []
    for i, job in enumerate(jobs):
        required_skills = set(
            skill.strip().lower() for skill in job.required_skills.split(",") if skill
        )

        matching_skills = resume_skills.intersection(required_skills)
        missing_skills = required_skills - resume_skills

        skill_match_percentage = (
            len(matching_skills) / len(required_skills) * 100
            if required_skills
            else 0
        )
        similarity_percentage = similarity_scores[i] * 100
        final_score = (0.6 * similarity_percentage) + (0.4 * skill_match_percentage)

        results.append(
            {
                "job_id": job.id,
                "title": job.title,
                "company": job.company,
                "similarity_score": round(similarity_percentage, 2),
                "skill_match_percentage": round(skill_match_percentage, 2),
                "missing_skills": list(missing_skills),
                "final_score": round(final_score, 2),
            }
        )

    results.sort(key=lambda x: x["final_score"], reverse=True)
    return results[:10]


# ---------- API ROUTES ----------

@app.post("/upload_resume/", response_model=dict)
async def upload_resume(file: UploadFile = File(...)):
    if file.filename.lower().endswith(".pdf"):
        resume_text = extract_text_from_pdf(file.file)
    elif file.filename.lower().endswith(".docx"):
        resume_text = extract_text_from_docx(file.file)
    else:
        raise HTTPException(status_code=400, detail="Only PDF and DOCX files are supported.")

    matched_jobs = match_jobs(resume_text)
    return {"matched_jobs": matched_jobs}


@app.post("/jobs/", response_model=Job)
def create_job(job: JobCreate, db: Session = Depends(get_db)):
    db_job = JobModel(**job.dict())
    db.add(db_job)
    db.commit()
    db.refresh(db_job)
    refresh_job_cache()
    return db_job


@app.get("/jobs/", response_model=List[Job])
def read_jobs(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(JobModel).offset(skip).limit(limit).all()


@app.get("/jobs/{job_id}", response_model=Job)
def read_job(job_id: int, db: Session = Depends(get_db)):
    job = db.query(JobModel).filter(JobModel.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@app.get("/healthz")
def health_check():
    return {"status": "ok"}