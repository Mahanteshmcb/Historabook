import whisper
import os
import warnings

# Suppress annoying warnings from the model
warnings.filterwarnings("ignore")

# We use the 'base' model. It's a good balance of speed/accuracy.
MODEL_SIZE = "base"
_model = None

def get_whisper_model():
    """Singleton: Load model once."""
    global _model
    if _model is None:
        print(f"👂 Loading Whisper ({MODEL_SIZE})... This happens once.")
        # This will download ~140MB the first time
        _model = whisper.load_model(MODEL_SIZE)
    return _model

def transcribe_audio(file_path: str) -> str:
    """
    Takes a path to a .wav/.mp3 file and returns the text.
    """
    if not os.path.exists(file_path):
        return ""
        
    model = get_whisper_model()
    
    # Run inference
    # fp16=False is safer for CPU usage
    result = model.transcribe(file_path, fp16=False)
    
    # FIX: Pylance thinks this is a list, so we force it to be a string
    text = str(result["text"]).strip()
    
    print(f"🗣️ User said: {text}")
    return text