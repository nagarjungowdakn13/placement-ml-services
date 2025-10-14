import shutil
import os

async def process_resume(file):
    upload_folder = "uploads"
    os.makedirs(upload_folder, exist_ok=True)
    file_path = os.path.join(upload_folder, file.filename)
    
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)
    
    # Dummy processing logic
    return {"filename": file.filename, "status": "processed"}
