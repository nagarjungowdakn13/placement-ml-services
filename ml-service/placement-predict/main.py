from fastapi import FastAPI, Body
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import random

app = FastAPI(title="Placement Prediction Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)


def predict_placement(skills: list) -> float:
    n = len(set(skills))
    # New heuristic: base = 0.08 * n, cap at 0.95, min 0.10, add small random factor
    base = max(0.10, min(0.08 * n, 0.95))
    noise = random.uniform(-0.05, 0.05)
    prob = max(0.10, min(base + noise, 0.95))
    return round(prob, 2)

@app.post("/predict-placement")
def predict(payload: dict = Body(...)):
    skills = [s for s in payload.get("skills", []) if isinstance(s, str)]
    prob = predict_placement(skills)
    return {"placement_probability": round(prob, 2)}

@app.get("/health")
def health():
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8003)
