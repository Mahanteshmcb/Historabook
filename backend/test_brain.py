from app.utils.embeddings import get_embedding
import time

print("Loading model... (this might take a minute)")
start = time.time()

# Test 1: Simple word
vec = get_embedding("Hello World")

print(f"Model loaded in {time.time() - start:.2f} seconds.")
print(f"Vector length: {len(vec)} (Should be 384)")
print(f"First 5 numbers: {vec[:5]}")

print("✅ AI Brain is working!")