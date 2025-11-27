from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from app.utils.tts_piper import generate_audio, AUDIO_DIR
import os

router = APIRouter()

class TTSRequest(BaseModel):
    text: str
    lang: str = "en" # Default to English

@router.post("/speak")
def text_to_speech(request: TTSRequest):
    # Pass the language code to the generator
    filename = generate_audio(request.text, request.lang)
    
    if filename == "error.wav":
        raise HTTPException(status_code=500, detail="TTS Generation failed. Check server logs for missing model files.")
        
    return {"audio_url": f"/api/audio/file/{filename}"}

@router.get("/file/{filename}")
def get_audio_file(filename: str):
    # Serve the file from the absolute path
    file_path = os.path.join(AUDIO_DIR, filename)
    
    if not os.path.exists(file_path):
        # Fallback check in current directory
        cwd_path = os.path.join(os.getcwd(), "static", "audio", filename)
        if os.path.exists(cwd_path):
            return FileResponse(cwd_path, media_type="audio/wav")
        raise HTTPException(status_code=404, detail="Audio file not found")
        
    return FileResponse(file_path, media_type="audio/wav")