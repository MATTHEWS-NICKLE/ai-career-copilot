import random
from sqlalchemy import create_engine, text

DATABASE_URL = "postgresql://postgres:root@localhost/ai_career_copilot"
engine = create_engine(DATABASE_URL)

job_titles = [
    "Machine Learning Engineer",
    "Data Scientist",
    "Backend Developer",
    "Frontend Developer",
    "Full Stack Developer",
    "Cloud Engineer",
    "DevOps Engineer",
    "AI Engineer",
    "Software Engineer",
    "Data Analyst"
]

companies = [
    "TechCorp",
    "InnovaTech",
    "FutureSoft",
    "NextGen Solutions",
    "CloudMatrix",
    "DataWorks",
    "Alpha Systems"
]

skills = [
    "python", "sql", "scikit-learn", "tensorflow",
    "node.js", "react", "aws", "docker",
    "kubernetes", "excel", "pandas"
]

def generate_description():
    selected = random.sample(skills, 4)
    return f"Looking for candidates skilled in {', '.join(selected)}."

with engine.connect() as conn:
    for _ in range(10000):  
        conn.execute(
            text("""
                INSERT INTO jobs (title, company, description, required_skills)
                VALUES (:title, :company, :description, :required_skills)
            """),
            {
                "title": random.choice(job_titles),
                "company": random.choice(companies),
                "description": generate_description(),
                "required_skills": ", ".join(random.sample(skills, 4))
            }
        )
    conn.commit()

print("Large dataset inserted successfully!")