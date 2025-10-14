#Resume Scoring & Job Matching
from fastapi import APIRouter, UploadFile, File
from app.services.feature3_service import score_resume

router = APIRouter()

@router.post("/score")
async def get_score(file: UploadFile = File(...)):
    score = await score_resume(file)
    return {"feature": "Feature3", "score": score}
