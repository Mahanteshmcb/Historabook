from sentence_transformers import SentenceTransformer

# Load model once (singleton pattern)
# This downloads about 80MB the first time you run it.
model = SentenceTransformer('all-MiniLM-L6-v2')

def get_embedding(text: str) -> list:
    """
    Converts text into a vector (list of 384 numbers).
    """
    if not text:
        return []
        
    # Model returns a numpy array, convert to list for JSON storage
    vector = model.encode(text)
    return vector.tolist()