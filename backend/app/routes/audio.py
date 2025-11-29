import os
import hashlib
import subprocess
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel

router = APIRouter()

# --- CONFIGURATION ---
CURRENT_FILE = os.path.abspath(__file__)
BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.dirname(CURRENT_FILE)))

AUDIO_DIR = os.path.join(BACKEND_DIR, "static", "audio")
os.makedirs(AUDIO_DIR, exist_ok=True)

# --- FIX: Accurate Path to Piper & Models ---
PIPER_ROOT = os.path.join(BACKEND_DIR, "app", "models", "llm_weights", "piper")
PIPER_EXE = os.path.join(PIPER_ROOT, "piper.exe")

# Point to the 'models' subfolder you showed in the screenshot
MODELS_DIR = os.path.join(PIPER_ROOT, "models")

# Select one of the models you have (e.g., Amy or LibriTTS)
# Let's default to 'en_US-libritts_r-medium.onnx' based on your file list
DEFAULT_MODEL_NAME = "en_US-libritts_r-medium.onnx"
MODEL_PATH = os.path.join(MODELS_DIR, DEFAULT_MODEL_NAME)

print(f"🔍 Piper EXE: {PIPER_EXE}")
print(f"🔍 Voice Model: {MODEL_PATH}")

class TTSRequest(BaseModel):
    text: str
    lang: str = "en"

@router.post("/speak")
def text_to_speech(request: TTSRequest):
    try:
        if not request.text:
            raise HTTPException(status_code=400, detail="No text provided")

        # 1. Cache Check
        text_hash = hashlib.md5(request.text.encode('utf-8')).hexdigest()
        filename = f"{text_hash}.wav"
        file_path = os.path.join(AUDIO_DIR, filename)

        if os.path.exists(file_path):
            print(f"⏩ Audio Cached: {filename}")
            return {"audio_url": f"/api/audio/file/{filename}"}

        # 2. Validation
        if not os.path.exists(PIPER_EXE):
             print(f"❌ Piper EXE missing at: {PIPER_EXE}")
             raise HTTPException(500, f"Piper EXE not found at {PIPER_EXE}")
        
        # Dynamic Model Selection (Optional: Switch based on lang)
        current_model = MODEL_PATH
        if request.lang.startswith("hi"): # Hindi support if requested
             hindi_model = os.path.join(MODELS_DIR, "hi_IN-pratham-medium.onnx")
             if os.path.exists(hindi_model):
                 current_model = hindi_model

        if not os.path.exists(current_model):
             print(f"❌ Voice Model missing at: {current_model}")
             raise HTTPException(500, f"Voice Model not found at {current_model}")

        # 3. Generation
        print(f"🎙️ Generating ({request.lang}): {request.text[:30]}...")
        
        proc = subprocess.run(
            [PIPER_EXE, "--model", current_model, "--output_file", file_path],
            input=request.text.encode('utf-8'),
            capture_output=True
        )
        
        if proc.returncode != 0:
            error_msg = proc.stderr.decode()
            print(f"❌ Piper Error: {error_msg}")
            raise Exception(f"Piper failed: {error_msg}")

        return {"audio_url": f"/api/audio/file/{filename}"}

    except Exception as e:
        print(f"TTS Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/file/{filename}")
def get_audio_file(filename: str):
    path = os.path.join(AUDIO_DIR, filename)
    if os.path.exists(path): return FileResponse(path)
    raise HTTPException(404, "File not found")