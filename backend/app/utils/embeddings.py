from sentence_transformers import SentenceTransformer
import os

# Load model once (singleton pattern)
# This downloads about 80MB the first time you run it.
# POINT TO THE LOCAL FOLDER
model_path = "./local_models/all-MiniLM-L6-v2"

# Check if it exists to be safe
if not os.path.exists(model_path):
    raise RuntimeError(f"Offline model not found at {model_path}. Please run download_model.py")

model = SentenceTransformer(model_path)

def get_embedding(text: str) -> list:
    """
    Converts text into a vector (list of 384 numbers).
    """
    if not text:
        return []
        
    # Model returns a numpy array, convert to list for JSON storage
    vector = model.encode(text)
    return vector.tolist()