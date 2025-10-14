# Resume Upload & Basic Info Extraction

from fastapi import APIRouter, UploadFile, File
from app.services.feature1_service import process_resume

router = APIRouter()


router = APIRouter()

@router.post("/upload")
async def upload_resume(file: UploadFile = File(...)):
    result = await process_resume(file)
    return {"feature": "Feature1", "result": result}
