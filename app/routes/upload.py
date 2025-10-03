from fastapi import APIRouter, UploadFile, File, HTTPException
import os
import uuid
from typing import Dict

router = APIRouter()

@router.post("/upload")
async def upload_csvs(
    students: UploadFile = File(...),
    courses: UploadFile = File(...),
    rooms: UploadFile = File(...),
    holidays: UploadFile = File(None)
):
    # Validate file extensions
    required_files = [(students, "students"), (courses, "courses"), (rooms, "rooms")]
    if holidays:
        required_files.append((holidays, "holidays"))
    
    for file, name in required_files:
        if file and not file.filename.endswith('.csv'):
            raise HTTPException(status_code=400, detail=f"{name} file must be CSV")
    
    # Save files with unique names
    saved_paths = {}
    for file, key in [(students, "students"), (courses, "courses"), (rooms, "rooms")]:
        unique_filename = f"{uuid.uuid4()}_{file.filename}"
        file_path = os.path.join("data", unique_filename)
        
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        saved_paths[key] = file_path
    
    # Handle optional holidays file
    if holidays:
        unique_filename = f"{uuid.uuid4()}_{holidays.filename}"
        file_path = os.path.join("data", unique_filename)
        
        with open(file_path, "wb") as f:
            content = await holidays.read()
            f.write(content)
        
        saved_paths["holidays"] = file_path
    
    return {"status": "ok", "paths": saved_paths}