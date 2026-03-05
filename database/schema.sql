-- SQL schema for AI Career Copilot
-- run this file against your Postgres instance if you prefer manual setup

CREATE TABLE IF NOT EXISTS jobs (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    company VARCHAR(255) NOT NULL,
    description TEXT,
    required_skills TEXT
);
