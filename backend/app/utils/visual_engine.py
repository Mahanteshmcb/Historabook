import torch
import os
import uuid
from diffusers.pipelines.auto_pipeline import AutoPipelineForText2Image
from app.utils.llm import unload_model as unload_llm 

# --- CONFIG ---
IMAGE_DIR = "static/images"
CURRENT_FILE_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.dirname(os.path.dirname(CURRENT_FILE_DIR))
ABSOLUTE_IMAGE_DIR = os.path.join(BACKEND_DIR, IMAGE_DIR)
os.makedirs(ABSOLUTE_IMAGE_DIR, exist_ok=True)

# Model initialization (Singleton Pattern)
_pipeline = None
MODEL_ID = "stabilityai/sd-turbo"
NUM_ANIMATION_FRAMES = 3 # Generate 3 frames for the slideshow effect

def get_visual_pipeline():
    """Loads the SD-Turbo model once, placing it on the GPU (cuda)."""
    global _pipeline
    if _pipeline is None:
        print("🖼️ Loading SD-Turbo Pipeline... (Approx 1GB VRAM)")
        device = "cuda" if torch.cuda.is_available() else "cpu"
        
        # Load the pipeline
        _pipeline = AutoPipelineForText2Image.from_pretrained(
            MODEL_ID, 
            torch_dtype=torch.float16,
            safety_checker=None
        ).to(device)

        _pipeline.scheduler.set_timesteps(2, device=device)

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

def generate_visual_draft(prompt: str) -> list[str]: # Returns a list of filenames
    """
    Generates multiple images (frames) for a prompt, swapping memory.
    """
    try:
        # 1. VRAM SWAP IN: UNLOAD LLM
        unload_llm()
        
        # 2. Load Visuals pipeline (SD-Turbo)
        pipeline = get_visual_pipeline()
        
        generated_filenames = []
        
        for i in range(NUM_ANIMATION_FRAMES):
            # Introduce slight variations for the animation effect
            variation_prompt = f"{prompt}, frame {i+1} of {NUM_ANIMATION_FRAMES}, subtle camera motion, depth of field"
            full_prompt = f"concept art, digital painting, cinematic, highly detailed, {variation_prompt}"
            
            # 3. Generate the image
            image = pipeline(
                full_prompt, 
                num_inference_steps=1, 
                guidance_scale=0.0 
            ).images[0]
            
            # 4. Save file
            filename = f"{uuid.uuid4()}_{i}.png" 
            filepath = os.path.join(ABSOLUTE_IMAGE_DIR, filename)
            image.save(filepath)
            generated_filenames.append(filename)
            
            print(f"✅ Generated Visual Frame {i+1}: {filename}")

        # 5. VRAM SWAP OUT: UNLOAD SD-TURBO
        unload_visual_pipeline()

        return generated_filenames

    except Exception as e:
        print(f"❌ VRAM CRASH/Visual Engine Error: {e}")
        return ["error.png"] # Return a list with error image