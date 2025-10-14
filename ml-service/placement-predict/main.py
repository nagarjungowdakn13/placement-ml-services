from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import joblib
import numpy as np
from sklearn.linear_model import LogisticRegression
import os
import uvicorn

app = FastAPI(title="Placement Prediction Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

model_path = "placement_model.pkl"
if not os.path.exists(model_path):
    X = np.array([
        [8.5, 0, 3, 1, 85, 80, 5],
        [7.0, 1, 1, 0, 70, 60, 2],
        [9.0, 0, 4, 2, 90, 85, 6]
    ])
    y = np.array([1, 0, 1])
    model = LogisticRegression()
    model.fit(X, y)
    joblib.dump(model, model_path)

model = joblib.load(model_path)

class StudentFeatures(BaseModel):
    cgpa: float
    dept: str
    projects: int
    internships: int
    aptitude_score: float
    interview_score: float
    skill_count: int

@app.post("/predict-placement")
def predict(features: StudentFeatures):
    dept_map = {"CSE": 0, "ECE": 1, "ME": 2}
    dept_val = dept_map.get(features.dept.upper(), 0)

    X = np.array([[features.cgpa, dept_val, features.projects,
                   features.internships, features.aptitude_score,
                   features.interview_score, features.skill_count]])
    
    prob = model.predict_proba(X)[0][1]
    return {"placement_probability": round(prob, 2)}

@app.get("/health")
def health():
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8003)
