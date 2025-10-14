CREATE DATABASE placement_db;

\c placement_db;

CREATE TABLE students (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255),
    cgpa FLOAT,
    department VARCHAR(50)
);

CREATE TABLE resumes (
    id SERIAL PRIMARY KEY,
    student_id INT REFERENCES students(id),
    file_path TEXT,
    skills TEXT[]
);

CREATE TABLE jobs (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255),
    company VARCHAR(255),
    description TEXT
);

CREATE TABLE student_job_interactions (
    id SERIAL PRIMARY KEY,
    student_id INT REFERENCES students(id),
    job_id INT REFERENCES jobs(id),
    score FLOAT
);

CREATE TABLE placement_predictions (
    id SERIAL PRIMARY KEY,
    student_id INT REFERENCES students(id),
    probability FLOAT
);

CREATE TABLE IF NOT EXISTS students (
  id SERIAL PRIMARY KEY,
  name VARCHAR(100),
  email VARCHAR(100),
  skills TEXT
);

CREATE TABLE IF NOT EXISTS jobs (
  id SERIAL PRIMARY KEY,
  title VARCHAR(100),
  description TEXT,
  skills_required TEXT
);
