from llama_cpp import Llama
import os
import re

# Your specific model path
MODEL_PATH = "app/models/llm_weights/phimini.gguf"

_model_instance = None

def get_model():
    """Singleton: Loads the model only once."""
    global _model_instance
    if _model_instance is None:
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(f"Model not found at {MODEL_PATH}")
            
        print("🤖 Loading Phi-3 LLM...")
        _model_instance = Llama(
            model_path=MODEL_PATH,
            n_ctx=4096,
            n_gpu_layers=-1, 
            verbose=False
        )
    return _model_instance

def unload_model():
    """Removes Phi-3 LLM from GPU/RAM to free VRAM."""
    global _model_instance
    if _model_instance is not None:
        print("🪓 Unloading Phi-3 LLM from memory...")
        del _model_instance
        _model_instance = None
        
        # PyTorch/CUDA cleanup
        try:
            import torch
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
        except ImportError:
            pass # Ignore if torch isn't used
        
def generate_narration(scene_content: str, characters: list) -> dict:
    llm = get_model()
    char_str = ", ".join(characters) if characters else "Unknown characters"
    
    # Prompt
    prompt = f"""<|system|>
You are a history teacher writing a script.
<|end|>
<|user|>
Scene: "{scene_content}"
Characters: {char_str}

Task:
1. Write a 1-sentence narration script.
2. Describe a visual for this scene.
3. Write one quiz question.

Use these exact labels:
NARRATION:
VISUAL:
QUIZ:
<|end|>
<|assistant|>"""

    # Run Inference
    output = llm(
        prompt, 
        max_tokens=256, 
        stop=["<|end|>"], 
        temperature=0.7,
        echo=False,
        stream=False  # <--- FIX 1: Explicitly disable streaming
    )
    
    # FIX 2: Add type: ignore because Pylance thinks this might be a stream
    text = output["choices"][0]["text"].strip() # type: ignore
    
    # Debug Print
    print(f"\n🤖 RAW AI OUTPUT:\n{text}\n{'='*20}")

    # Smarter Parsing (Regex)
    narration_match = re.search(r'NARRATION:?\s*(.*?)(?=VISUAL:|QUIZ:|$)', text, re.I | re.S)
    visual_match = re.search(r'VISUAL:?\s*(.*?)(?=NARRATION:|QUIZ:|$)', text, re.I | re.S)
    quiz_match = re.search(r'QUIZ:?\s*(.*?)(?=NARRATION:|VISUAL:|$)', text, re.I | re.S)

    parsed = {
        "narration": narration_match.group(1).strip() if narration_match else "",
        "visual": visual_match.group(1).strip() if visual_match else "",
        "quiz": quiz_match.group(1).strip() if quiz_match else ""
    }
            
    # Fallbacks
    if not parsed["narration"]: parsed["narration"] = "Let's examine this scene in detail."
    if not parsed["visual"]: parsed["visual"] = "A historical setting."
    
    return parsed