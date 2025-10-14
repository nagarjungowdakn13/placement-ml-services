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
