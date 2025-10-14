from fastapi import FastAPI, Body
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from typing import List, Dict
import os, json, logging

logger = logging.getLogger("collaborative-filter")
logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO").upper(), format="[%(asctime)s] %(levelname)s %(name)s: %(message)s")

app = FastAPI(title="Collaborative Filtering Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

DEFAULT_CATALOG_PATH = os.getenv("JOB_CATALOG_PATH", os.path.join(os.path.dirname(__file__), "job_catalog.json"))

def load_catalog(path: str = DEFAULT_CATALOG_PATH) -> Dict[str, List[str]]:
    try:
        with open(path, "r", encoding="utf-8") as f:
            catalog = json.load(f)
        logger.info("Loaded job catalog entries=%d path=%s", len(catalog), path)
        return catalog
    except Exception as e:
        logger.warning("Failed to load job catalog at %s: %s", path, e)
        return {
            "Data Analyst": ["python", "sql", "pandas", "excel"],
            "Backend Developer": ["node.js", "express", "sql", "docker"],
        }

JOB_CATALOG = load_catalog()

@app.post("/recommendations")
def recommend_jobs(payload: dict = Body(...), top_n: int = 5):
    user_skills: List[str] = [s for s in payload.get("skills", []) if isinstance(s, str)]
    skillset = {s.strip().lower() for s in user_skills if s.strip()}
    if not skillset:
        return {"recommendations": []}

    scored = []
    for job, tags in JOB_CATALOG.items():
        tagset = {t.lower() for t in tags}
        overlap = len(skillset & tagset)
        if overlap:
            scored.append((job, overlap, len(tagset)))

    # sort by overlap desc then coverage ratio desc
    scored.sort(key=lambda x: (x[1], x[1]/x[2] if x[2] else 0), reverse=True)
    recs = [j for j, _, _ in scored[:top_n]]
    logger.info("Recommendations computed count=%d", len(recs))
    return {"recommendations": recs}

@app.get("/diagnostics")
def diagnostics():
    return {"catalog_size": len(JOB_CATALOG), "sample": list(JOB_CATALOG.keys())[:10]}

@app.post("/reload-catalog")
def reload_catalog():
    global JOB_CATALOG
    JOB_CATALOG = load_catalog()
    return {"reloaded": True, "catalog_size": len(JOB_CATALOG)}

@app.get("/health")
def health():
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8002)
