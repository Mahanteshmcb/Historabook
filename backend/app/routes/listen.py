from fastapi import APIRouter, UploadFile, File, HTTPException
from app.utils.stt import transcribe_audio
import shutil
import os
import uuid

router = APIRouter()

# Temp folder for uploads
UPLOAD_DIR = "static/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/transcribe")
def listen_to_user(file: UploadFile = File(...)):
    """
    Receives an audio blob, saves it, and runs Whisper.
    """
    # 1. Save the uploaded audio to a temp file
    # We give it a unique name so multiple users don't clash
    filename = f"{uuid.uuid4()}.wav"
    file_path = os.path.join(UPLOAD_DIR, filename)
    
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # 2. Run Whisper
        text = transcribe_audio(file_path)
        
        # 3. Cleanup (Delete the file to save space)
        # We wrap this in try/except just in case file is locked
        try:
            os.remove(file_path)
        except:
            pass
        
        return {"text": text}
        
    except Exception as e:
        print(f"❌ Transcription Error: {e}")
        # Common error: ffmpeg not installed
        if "ffmpeg" in str(e).lower():
            raise HTTPException(status_code=500, detail="Server missing FFMPEG. Cannot process audio.")
        raise HTTPException(status_code=500, detail=str(e))