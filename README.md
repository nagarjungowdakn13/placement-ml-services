# Placement Website - Microservices

This project provides three core features as independent microservices with a Node.js API gateway and a React frontend:

- Skill extraction from resumes (PDF/DOCX/Image w/ OCR) (Python FastAPI)
- Job recommendation via skill-overlap scoring (Python FastAPI)
- Placement prediction heuristic (Python FastAPI)

The Node backend proxies requests to these services; the frontend consumes the backend endpoints.

## Services and Ports

- Backend (Node/Express): http://localhost:5000
- Frontend (React/Vite): http://localhost:3000
- Resume NLP: http://localhost:8001
- Collaborative Filter: http://localhost:8002
- Placement Predict: http://localhost:8003
- Postgres: localhost:5432

## Quick start (local without Docker)

1. Copy env

```
copy .env.example .env
```

2. Start Python services (3 terminals)

```
# Resume NLP
cd ml-service\resume-nlp && pip install -r requirements.txt && uvicorn main:app --host 0.0.0.0 --port 8001

# Collaborative Filter
cd ml-service\collaborative-filter && pip install -r requirements.txt && uvicorn main:app --host 0.0.0.0 --port 8002

# Placement Predict
cd ml-service\placement-predict && pip install -r requirements.txt && uvicorn main:app --host 0.0.0.0 --port 8003
```

3. Start backend

```
cd backend && npm install && npm run dev
```

4. Start frontend

```
cd frontend && npm install && npm run dev
```

## Run with Docker

```
docker compose up --build
```

Services will be available on the same ports listed above.

## API contracts (Gateway)

- POST /api/resumes/upload
  - form-data: resume (file field name: `resume`)
  - returns: `{ skills: string[] }`
- POST /api/jobs/recommend?top_n=5
  - body: `{ skills: string[] }`
  - returns: `{ recommendations: string[] }`
- POST /api/placement
  - body: `{ skills: string[] }`
  - returns: `{ placement_probability: number }`

## Service maintenance endpoints

Resume NLP:

- GET http://localhost:8001/diagnostics
- POST http://localhost:8001/reload-corpus (reloads `skill_corpus.txt`)

Collaborative Filter:

- GET http://localhost:8002/diagnostics
- POST http://localhost:8002/reload-catalog (reloads `job_catalog.json`)

## Notes

- Skill corpus externalized: `ml-service/resume-nlp/skill_corpus.txt` (override path via `SKILL_CORPUS_PATH`).
- Job catalog externalized: `ml-service/collaborative-filter/job_catalog.json` (override via `JOB_CATALOG_PATH`).
- Resume NLP uses fuzzy matching (RapidFuzz). spaCy is optional; absence just triggers simple tokenization.
- Image OCR requires Tesseract installed locally (see below) plus `pytesseract` Python lib.
- Placement prediction is a heuristic on unique skill count (placeholder for a real model).
- Frontend allows manual skill add and clear-all; edits immediately re-trigger recommendations & placement.

### Installing Tesseract (Windows)

Options:

1. Chocolatey (admin PowerShell):

```powershell
choco install tesseract -y
```

2. Scoop:

```powershell
scoop install tesseract
```

3. Manual: Download installer from https://github.com/tesseract-ocr/tesseract and add install dir (e.g. `C:\Program Files\Tesseract-OCR`) to PATH.

If installed in a non-standard path, set environment variable before starting the service:

```
set TESSDATA_PREFIX=C:\Program Files\Tesseract-OCR\tessdata
```

### Environment variables

| Variable          | Service              | Purpose                   | Default                         |
| ----------------- | -------------------- | ------------------------- | ------------------------------- |
| SKILL_CORPUS_PATH | resume-nlp           | Path to skill corpus file | skill_corpus.txt in service dir |
| JOB_CATALOG_PATH  | collaborative-filter | Path to job catalog JSON  | job_catalog.json in service dir |
| LOG_LEVEL         | all python services  | Logging level             | INFO                            |

After editing corpus/catalog files you can POST to reload endpoints (see maintenance section) without restarting containers.

## Troubleshooting

- Ensure the three Python services are running before the backend.
- If uploads fail, verify multipart form uses field name `resume` (gateway maps to NLP service field `file`).
- Empty skill list? Check /diagnostics for corpus size; maybe corpus path incorrect.
- OCR returning no text: confirm Tesseract installed & in PATH; try a higher quality image.
- Change in corpus or catalog not reflected: call reload endpoint.
- For Windows path issues, avoid spaces in path names where possible.
