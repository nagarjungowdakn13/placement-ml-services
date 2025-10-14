from fastapi import FastAPI, Body
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI(title="Placement Prediction Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)


@app.post("/predict-placement")
def predict(payload: dict = Body(...)):
    skills = [s for s in payload.get("skills", []) if isinstance(s, str)]
    # Simple probability based on unique skills recognized; 6% per skill, cap at 100%
    prob = min(1.0, 0.06 * len(set([s.strip().lower() for s in skills])))
    return {"placement_probability": round(prob, 2)}

@app.get("/health")
def health():
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8003)
