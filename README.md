# AI Career Copilot 🚀

AI Career Copilot is an intelligent Resume–Job Matching System that analyzes uploaded resumes (PDF or DOCX) and compares them against a large PostgreSQL job database.

The system provides:

* Similarity Score (%)
* Skill Match Percentage (%)
* Missing Skills Recommendation
* Final Weighted Score (Ranking)

This project supports bulk job data using a database instead of CSV files and includes a simple frontend interface for resume upload and result display.

---

# Features

* Upload Resume (PDF / DOCX)
* Automatic text extraction
* Semantic similarity using TF-IDF
* Skill-based matching
* Missing skill suggestions
* Weighted final ranking
* PostgreSQL database (handles large data)
* Simple frontend UI for interaction

---

# Tech Stack

Backend:

* FastAPI
* PostgreSQL
* SQLAlchemy
* Scikit-learn
* pdfplumber
* python-docx

Frontend:

* HTML
* CSS
* JavaScript (Fetch API)

---

# Project Structure

```
ai-career-copilot/
│
├── app.py
├── bulk_jobs.py
├── index.html
├── README.md
└── requirements.txt
```

---

# Database Setup

Create database:

```sql
CREATE DATABASE ai_career_copilot;
```

Connect:

```sql
\c ai_career_copilot
```

Create jobs table:

```sql
CREATE TABLE jobs (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255),
    company VARCHAR(255),
    description TEXT,
    required_skills TEXT
);
```

Example required_skills format:

```
python, machine learning, sql, pandas, fastapi
```

---

# Installation & Run

1. Create virtual environment

```
python -m venv venv
```

Activate:

Windows:

```
venv\Scripts\activate
```

Mac/Linux:

```
source venv/bin/activate
```

2. Install dependencies

```
pip install fastapi uvicorn sqlalchemy psycopg2-binary scikit-learn pdfplumber python-docx python-multipart
```

3. Update database URL in `app.py`

```
DATABASE_URL = "postgresql://postgres:yourpassword@localhost/ai_career_copilot"
```

4. Run backend

```
uvicorn app:app --reload
```

Server runs at:

```
http://127.0.0.1:8000
```

---

# Frontend Setup

The project includes a simple `index.html` file.

To run frontend:

* Simply open `index.html` in your browser
  OR
* Use Live Server (VS Code recommended)

The frontend allows:

* Resume upload
* Sending file to FastAPI backend
* Displaying job results in table format

---

# How It Works

1. User uploads resume (PDF or DOCX)
2. Text is extracted from resume
3. TF-IDF converts resume and job descriptions into vectors
4. Cosine similarity calculates semantic match
5. Resume skills are compared with required job skills
6. Final Score is calculated:

Final Score = (0.6 × Similarity %) + (0.4 × Skill Match %)

7. Top 10 ranked jobs are displayed on frontend

---

# Example Output

Title: Data Scientist
Company: TechCorp
Similarity: 82%
Skill Match: 70%
Missing Skills: deep learning, aws
Final Score: 77%

---

# Why Use PostgreSQL Instead of CSV?

* Handles large-scale job data
* Faster and efficient querying
* Scalable architecture
* Production-ready design

---

# Future Improvements

* Use Sentence Transformers instead of TF-IDF
* Add Resume Improvement Suggestions
* Add Authentication System
* Deploy with Docker
* Build advanced React frontend

---

AI Career Copilot is suitable for:

* Final Year Projects
* Portfolio Projects
* AI Career Platforms
* Startup MVP Development
