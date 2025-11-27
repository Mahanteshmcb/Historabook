import os
import subprocess
import uuid

# --- CONFIG ---
# Paths relative to this file (backend/app/utils/tts_piper.py)
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
# Go up 2 levels to 'backend'
BACKEND_DIR = os.path.dirname(os.path.dirname(CURRENT_DIR))

# FIX: Update paths to match where you placed the files
# Location: backend/app/models/llm_weights/piper/
PIPER_BASE_DIR = os.path.join(BACKEND_DIR, "app", "models", "llm_weights", "piper")

PIPER_EXE = os.path.join(PIPER_BASE_DIR, "piper.exe")
MODELS_DIR = os.path.join(PIPER_BASE_DIR, "models")

# Output folder (still in static/audio)
AUDIO_DIR = os.path.join(BACKEND_DIR, "static", "audio")
os.makedirs(AUDIO_DIR, exist_ok=True)

# Map language codes to filenames
VOICE_MAP = {
    "en": "en_US-libritts_r-medium.onnx",
    "hi-fe": "hi_IN-priyamvada-medium.onnx", 
    "hi-ma": "hi_IN-pratham-medium.onnx",
    "sa": "sa_IN-google-medium.onnx"
}

def generate_audio(text: str, lang: str = "en") -> str:
    """
    Runs Piper.exe via subprocess to generate audio.
    """
    # 1. Check if Piper tool exists
    if not os.path.exists(PIPER_EXE):
        print(f"❌ Piper EXE not found at: {PIPER_EXE}")
        return "error.wav"

    # 2. Find the correct model file for the language
    model_filename = VOICE_MAP.get(lang, VOICE_MAP["en"])
    model_path = os.path.join(MODELS_DIR, model_filename)
    
    if not os.path.exists(model_path):
        print(f"❌ Voice Model not found for '{lang}': {model_path}")
        return "error.wav"

    # 3. Prepare Output Path
    filename = f"{uuid.uuid4()}.wav"
    output_path = os.path.join(AUDIO_DIR, filename)

    try:
        # Command: echo "text" | piper.exe -m model.onnx -f file.wav
        cmd = [
            PIPER_EXE,
            "--model", model_path,
            "--output_file", output_path
        ]

        # 4. Run the process
        process = subprocess.Popen(
            cmd, 
            stdin=subprocess.PIPE, 
            stdout=subprocess.DEVNULL, 
            stderr=subprocess.DEVNULL
        )
        process.communicate(input=text.encode('utf-8'))
        
        print(f"✅ Piper Generated ({lang}): {filename}")
        return filename

    except Exception as e:
        print(f"❌ Piper Critical Error: {e}")
        return "error.wav"