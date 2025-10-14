#Extract Skills
from fastapi import APIRouter, UploadFile, File
from app.services.feature2_service import extract_skills

router = APIRouter()

@router.post("/skills")
async def get_skills(file: UploadFile = File(...)):
    skills = await extract_skills(file)
    return {"feature": "Feature2", "skills": skills}
