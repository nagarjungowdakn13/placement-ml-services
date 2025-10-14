from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
import uvicorn

app = FastAPI(title="Collaborative Filtering Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

interaction_matrix = pd.DataFrame({
    "jobA": [1, 1, 0],
    "jobB": [0, 1, 1],
    "jobC": [1, 0, 1],
    "jobD": [0, 0, 0]
}, index=["student1", "student2", "student3"])

@app.get("/recommendations/{student_id}")
def recommend_jobs(student_id: str, top_n: int = 5):
    if student_id not in interaction_matrix.index:
        return {"error": "student not found"}

    student_vector = interaction_matrix.loc[student_id].values.reshape(1, -1)
    similarities = cosine_similarity(student_vector, interaction_matrix.values)[0]

    scores = pd.Series(similarities, index=interaction_matrix.index).drop(student_id)
    job_scores = {}
    for other_student, sim in scores.items():
        for job, interacted in interaction_matrix.loc[other_student].items():
            if interacted > 0:
                job_scores[job] = job_scores.get(job, 0) + sim * interacted

    top_jobs = sorted(job_scores.items(), key=lambda x: x[1], reverse=True)[:top_n]
    return {"recommendations": [job for job, _ in top_jobs]}

@app.get("/health")
def health():
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8002)
