# Placement Website - Microservices

This project provides three core features as independent microservices with a Node.js API gateway and a React frontend:

- Skill extraction from resume (Python FastAPI)
- Job recommendation using collaborative filtering (Python FastAPI)
- Placement prediction (Python FastAPI)

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

## API contracts

- POST /api/resumes/upload

  - form-data: resume (file)
  - returns: { skills: string[] }

- GET /api/jobs/recommend/:studentId?top_n=5

  - returns: { recommendations: string[] }

- POST /api/placement
  - body: { cgpa:number, dept:string, projects:number, internships:number, aptitude_score:number, interview_score:number, skill_count:number }
  - returns: { placement_probability: number }

## Notes

- The Resume NLP service uses fuzzy matching against a curated skills list. SpaCy is optional; if the model isn't available, it falls back to basic tokenization.
- The collaborative filter uses a static interaction matrix for demo purposes; replace with your data.
- The placement model trains a simple Logistic Regression demo model on first run and persists to a pickle.

## Troubleshooting

- Ensure the three Python services are running before the backend.
- If uploads fail, verify the backend sends multipart/form-data and the NLP service receives field name `file`.
- For Windows path issues, avoid spaces in path names where possible.

## Deploying to Render (recommended)

This repo includes a Render blueprint (`render.yaml`) to deploy all 5 services:
- Frontend: static site (Vite build)
- Backend: Node/Express
- Resume NLP: Python/FastAPI
- Collaborative Filter: Python/FastAPI
- Placement Predict: Python/FastAPI

Steps:
1. Push this repo to your GitHub (public or private).
2. Create a Render account at https://render.com and connect your GitHub.
3. Click New → Blueprint, pick this repository.
4. Accept the defaults; ensure all five services are listed.
5. Deploy. Render will build and start each service.

After deploy, grab the service URLs from the Render dashboard:
- Backend (placement-backend): https://PLACEMENT-BACKEND-SUBDOMAIN.onrender.com
- Resume NLP: https://RESUME-NLP-SUBDOMAIN.onrender.com
- Collaborative Filter: https://COLLABORATIVE-FILTER-SUBDOMAIN.onrender.com
- Placement Predict: https://PLACEMENT-PREDICT-SUBDOMAIN.onrender.com
- Frontend (placement-frontend): https://PLACEMENT-FRONTEND-SUBDOMAIN.onrender.com

Notes:
- The blueprint sets VITE_API_URL for the static Frontend to point to `https://placement-backend.onrender.com`.
  - If your backend URL differs, update the Frontend service Env Var `VITE_API_URL` to the actual backend URL and redeploy.
- The backend picks up the ML service URLs via env vars in the blueprint; if your ML service names differ, update them and redeploy.
- Health checks are exposed for all services at `/health`.
- Free plan may sleep services when idle; first request may be cold.

Verification after deployment:
- Backend: `GET /health` → `{ "status": "ok" }`
- Frontend: load the URL and interact with the three features.
- Endpoints: use the `tests/smoke.http` file with updated base URLs.
