import os
from sentence_transformers import SentenceTransformer

# 1. Define where to save it (inside your backend folder)
model_path = "./local_models/all-MiniLM-L6-v2"

print(f"⏳ Downloading model to {model_path}...")

# 2. Download and save to that specific folder
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
model.save(model_path)

print("✅ Model saved locally! You can now go offline.")