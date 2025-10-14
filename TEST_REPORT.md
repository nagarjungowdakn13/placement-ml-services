# Test Report – Placement Microservices Project

Date: 2025-10-13

## Scope

This report documents how the application was verified locally (without Docker) across all three core features:

- Skill extraction from resume
- Job recommendation using collaborative filtering
- Placement prediction

It covers the environment used, architecture, test endpoints, manual smoke tests, edge cases, and results.

## Environment

- OS: Windows
- Shell: cmd.exe
- Node.js: v22.16.0 (npm 10.9.2)
- Python: 3.14.0 (user site-packages used)
- Services and ports
  - Backend (Node/Express): http://localhost:5000
  - Frontend (Vite React): http://localhost:3000
  - Resume NLP (FastAPI): http://localhost:8001
  - Collaborative Filter (FastAPI): http://localhost:8002
  - Placement Predict (FastAPI): http://localhost:8003

Environment variables (root .env)

- NLP_SERVICE_URL=http://localhost:8001
- CF_SERVICE_URL=http://localhost:8002
- PLACEMENT_SERVICE_URL=http://localhost:8003
- VITE_API_URL=http://localhost:5000

## What we used

- Backend gateway: Express + Axios + Multer + TypeScript
- ML services: FastAPI + Uvicorn
  - Resume NLP: rapidfuzz; optional SpaCy fallback disabled by default for faster setup
  - Collaborative Filter: numpy/pandas + sklearn cosine similarity
  - Placement Predict: sklearn LogisticRegression (simple demo model persisted on first run)
- Frontend: React (Vite) calling backend routes
- curl (manual HTTP testing)

## How it works (data flow)

- Frontend → Backend (API gateway) → ML services
  - Resume upload: Browser posts multipart/form-data (field name `resume`) to `POST /api/resumes/upload`.
    - Backend streams the file buffer to Resume NLP `POST /parse`.
    - NLP extracts skills via fuzzy matching and returns `{ skills: string[] }`.
  - Job recommendations: Browser invokes `GET /api/jobs/recommend/:studentId`.
    - Backend proxies to CF `GET /recommendations/:student_id?top_n=N`.
  - Placement prediction: Browser invokes `POST /api/placement` with student features.
    - Backend proxies to Placement service `POST /predict-placement`.

## Endpoints under test

- Backend
  - GET /health → { status: "ok" }
  - POST /api/resumes/upload (multipart/form-data; field `resume`) → { skills: string[] }
  - GET /api/jobs/recommend/:studentId?top_n=5 → { recommendations: string[] }
  - POST /api/placement (JSON body) → { placement_probability: number }
- ML services
  - GET /health for all 3 services

## Manual smoke tests (cmd.exe)

1. Backend health

```
curl -s http://localhost:5000/health
```

Expected: {"status":"ok"}

2. Job recommendations

```
curl -s http://localhost:5000/api/jobs/recommend/student1
```

Expected: {"recommendations":["jobB","jobA","jobC"]}

3. Placement prediction

```
curl -s -X POST http://localhost:5000/api/placement -H "Content-Type: application/json" -d "{\"cgpa\":8.5,\"dept\":\"CSE\",\"projects\":3,\"internships\":1,\"aptitude_score\":85,\"interview_score\":80,\"skill_count\":5}"
```

Expected (demo model): {"placement_probability":0.99}

4. Resume skills (use a file containing known skills)

```
REM Create a temp file with some skills
> echo Python React SQL > %TEMP%\resume.txt
curl -s -F "resume=@%TEMP%\resume.txt" http://localhost:5000/api/resumes/upload
```

Expected: skills array includes items like ["Python","React","SQL"] (order may vary)

5. Frontend check

- Open http://localhost:3000 and verify:
  - Resume upload form works and shows parsed skills for a skills-containing file
  - Recommended jobs lists items for student1
  - Placement probability displays a percentage

## Edge cases tested

- GET against POST-only routes now returns 405 JSON with guidance
  - /api/resumes/upload (GET) → 405 with “Use POST … multipart/form-data”
  - /api/placement (GET) → 405 with “Use POST … JSON body”
- Missing file on resume upload → 400 with { error: "No file uploaded" }
- Unknown student in recommender → returns { error: "student not found" } from CF
- NLP service fuzzy matching returns [] if no known skills present in text
- Timeouts: gateway requests to ML services use 5–10s timeouts

## Results

- Backend and all ML services responded as expected.
- Frontend served via Vite on port 3000 and displayed all three features.
- Example successful responses observed:
  - GET /api/jobs/recommend/student1 → ["jobB","jobA","jobC"]
  - POST /api/placement → 0.99
  - POST /api/resumes/upload with text "Python React SQL" → non-empty skills list

## Known limitations

- Resume NLP uses a curated skills list + fuzzy match; real-world resumes benefit from proper NLP pipelines (SpaCy model, OCR for PDFs).
- Collaborative filtering uses demo interaction data; replace with real interactions for meaningful results.
- The frontend is a simple dashboard; no routing/state management beyond essentials.

## Next steps (optional)

- Add automated tests
  - Backend (Jest + supertest) for routes
  - ML services (pytest) for endpoints and model logic
- Docker healthchecks and GitHub Actions CI
- Upgrade multer to 2.x (1.x deprecated)

---

For quick REST testing in VS Code, see `tests/smoke.http`.
