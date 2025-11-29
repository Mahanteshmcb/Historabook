import torch
import os
import hashlib
from diffusers.pipelines.auto_pipeline import AutoPipelineForText2Image
from app.utils.llm import unload_model as unload_llm 

# --- CONFIG ---
IMAGE_DIR = "static/images"

# 1. Get the directory of THIS file (backend/app/utils)
current_dir = os.path.dirname(os.path.abspath(__file__))

# 2. Go up TWO levels to get to 'backend' (app -> utils -> backend)
BACKEND_DIR = os.path.normpath(os.path.join(current_dir, "..", ".."))

# 3. Define the Image Directory
ABSOLUTE_IMAGE_DIR = os.path.join(BACKEND_DIR, "static", "images")
os.makedirs(ABSOLUTE_IMAGE_DIR, exist_ok=True)

# 4. Define the Model Path relative to backend
MODEL_PATH = os.path.join(BACKEND_DIR, "local_models", "sd-turbo")

# --- DEBUG: Print the paths so we can see them ---
print(f"📂 DEBUG Project Path: {BACKEND_DIR}")
print(f"📂 DEBUG Model Path:   {MODEL_PATH}")

# Global variables
_pipeline = None
NUM_ANIMATION_FRAMES = 3 

def get_visual_pipeline():
    """Loads the SD-Turbo model from LOCAL STORAGE."""
    global _pipeline
    if _pipeline is None:
        print(f"🖼️ Loading SD-Turbo...")
        
        # Check if model exists
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(f"❌ Model missing at {MODEL_PATH}. Run 'python download_visuals.py' first!")

        device = "cuda" if torch.cuda.is_available() else "cpu"
        
        # Load OFFLINE
        try:
            _pipeline = AutoPipelineForText2Image.from_pretrained(
                MODEL_PATH, 
                torch_dtype=torch.float16,
                safety_checker=None,
                local_files_only=True, # Forces offline mode
                use_safetensors=True
            ).to(device)

            _pipeline.scheduler.set_timesteps(2, device=device)
        except Exception as e:
            print(f"❌ Error loading visual model: {e}")
            raise e

    return _pipeline

def unload_visual_pipeline():
    """Unloads the SD-Turbo model."""
    global _pipeline
    if _pipeline is not None:
        print("🪓 Unloading SD-Turbo from memory...")
        del _pipeline
        _pipeline = None
        import torch
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

def generate_visual_draft(prompt: str) -> list[str]: 
    """
    Generates multiple images (frames).
    UPDATE: Uses Prompt Hashing to cache images.
    """
    try:
        # 1. SMART CACHE CHECK
        # Create a unique filename based on the text prompt
        prompt_hash = hashlib.md5(prompt.encode('utf-8')).hexdigest()
        
        cached_filenames = []
        all_cached = True
        
        # Check if we already have frames for this prompt
        for i in range(NUM_ANIMATION_FRAMES):
            filename = f"{prompt_hash}_{i}.png"
            filepath = os.path.join(ABSOLUTE_IMAGE_DIR, filename)
            if os.path.exists(filepath):
                cached_filenames.append(filename)
            else:
                all_cached = False
                break
        
        if all_cached:
            print(f"⏩ Skipping generation (Cached): {prompt_hash[:8]}...")
            return cached_filenames

        # 2. GENERATION (If not cached)
        # VRAM SWAP IN: UNLOAD LLM
        unload_llm()
        
        # Load Visuals pipeline (SD-Turbo)
        pipeline = get_visual_pipeline()
        
        generated_filenames = []
        
        for i in range(NUM_ANIMATION_FRAMES):
            variation_prompt = f"{prompt}, frame {i+1} of {NUM_ANIMATION_FRAMES}, subtle camera motion"
            full_prompt = f"cinematic, highly detailed, {variation_prompt}"
            
            image = pipeline(
                full_prompt, 
                num_inference_steps=1, 
                guidance_scale=0.0 
            ).images[0]
            
            # Save file with HASH name (Deterministic)
            filename = f"{prompt_hash}_{i}.png" 
            filepath = os.path.join(ABSOLUTE_IMAGE_DIR, filename)
            image.save(filepath)
            generated_filenames.append(filename)
            
            print(f"✅ Generated: {filename}")

        # 5. DO NOT UNLOAD (Keep ready for next scene)
        # unload_visual_pipeline()

        return generated_filenames

    except Exception as e:
        print(f"❌ Visual Engine Error: {e}")
        return ["error.png"]