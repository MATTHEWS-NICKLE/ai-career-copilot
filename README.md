# AI Career Copilot 🚀

AI Career Copilot is an intelligent Resume–Job Matching System that analyzes uploaded resumes (PDF or DOCX) and compares them against a large PostgreSQL job database.

The system provides:

* Similarity Score (%)
* Skill Match Percentage (%)
* Missing Skills Recommendation
* Final Weighted Score (Ranking)

This project supports bulk job data using a database instead of CSV files and includes a simple frontend interface with job management and resume upload.  A lightweight Express proxy is provided so the UI and API can run from the same origin.

---

# Features

* Upload Resume (PDF / DOCX)
* Automatic text extraction
* Semantic similarity using TF-IDF
* Skill-based matching
* Missing skill suggestions
* Weighted final ranking
* PostgreSQL database (handles large data)
* Simple frontend UI for interaction with job CRUD and resume analysis

---

# Tech Stack

Backend:

* FastAPI
* PostgreSQL (optional)
* SQLite (fallback for local use)
* SQLAlchemy ORM
* Pydantic schemas
* Scikit-learn
* pdfplumber
* python-docx
* python-multipart

Frontend:

* HTML
* CSS
* JavaScript (Fetch API) with Express proxy

---

# Project Structure

```
ai-career-copilot/
│
├── backend/
│   ├── app.py
│   ├── bulk_insert_jobs.py
│   └── requirements.txt
├── frontend/
│   ├── package.json
│   ├── server.js
│   └── public/
│       └── index.html
└── README.md
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

> If you do not want to use PostgreSQL, the backend will use a local SQLite file by default when `DATABASE_URL` is not set.

Example required_skills format:

```
python, machine learning, sql, pandas, fastapi
```

---

# Installation & Run

1. Create a Python virtual environment and activate it (see your platform's instructions).

2. Install backend dependencies:

```
pip install -r backend/requirements.txt
```

3. Install root npm dependencies so `npm run dev` works:

```
npm install
```

4. By default, the backend will use a local SQLite database at `backend/ai_career_copilot.db` if `DATABASE_URL` is not set. On first startup, it seeds sample job data automatically when the database is empty.

5. Start the full app from the repo root with:

```
npm run dev
```

This runs both backend and frontend together.

6. If you prefer PowerShell scripts instead, use:

```
./run-backend.ps1
./run-frontend.ps1
```

The API will be available at `http://127.0.0.1:8000` and the UI at `http://localhost:3000`.

If you are not using PowerShell, you can also run the backend directly with:

```
.\.venv\Scripts\python.exe -m uvicorn backend.app:app --reload --host 127.0.0.1 --port 8000
```

And start the frontend directly with:

```
cd frontend
node server.js
```

The UI is then served at `http://localhost:3000`.

---

# Frontend Setup

This project includes a simple `index.html` file served via `frontend/server.js`. You can start the frontend by installing dependencies (`npm install`) and running `npm start`.

The UI provides:

* Resume upload with progress indicator
* Job creation and listing
* Dynamic display of results returned by the backend
* All API requests are proxied through Express to avoid CORS issues

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

* Replace TF-IDF with transformer embeddings (e.g. Sentence-BERT)
* Add resume feedback and auto-skill estimates
* Add authentication and user accounts
* Allow editing/deleting jobs from the UI
* Move cache out of process to Redis for horizontal scaling
* Add unit tests and CI pipeline

* Add Authentication System
* Deploy with Docker
* Build advanced React frontend
