from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.utils.visual_engine import generate_visual_draft, ABSOLUTE_IMAGE_DIR
from fastapi.responses import FileResponse
from typing import List, Optional
import os

router = APIRouter()

# --- DAY 32 UPDATE: Enhanced Request Schema ---
class VisualRequest(BaseModel):
    prompt: str
    style: str = "cinematic"
    character_focus: Optional[str] = None

class VisualResponse(BaseModel):
    image_urls: List[str]

@router.post("/generate", response_model=VisualResponse)
def generate_draft(request: VisualRequest):
    """
    Day 32: Receives full Visual Spec to construct a better prompt.
    """
    if not request.prompt:
        raise HTTPException(status_code=400, detail="Prompt required.")

    # Construct a rich prompt based on the spec
    # This helps consistency (Day 33/45 goal)
    full_prompt = request.prompt
    
    if request.character_focus:
        full_prompt = f"focus on {request.character_focus}, {full_prompt}"
        
    # Append style modifiers
    if request.style == "cinematic":
        full_prompt += ", cinematic lighting, 8k, detailed, depth of field"
    elif request.style == "sketch":
        full_prompt += ", pencil sketch, rough style, concept art"
    else:
        full_prompt += f", {request.style}"

    print(f"🎨 Generating Visual: '{full_prompt}'")

    # Get the list of filenames from the generation utility
    filenames = generate_visual_draft(full_prompt) 
    
    if filenames == ["error.png"]:
        raise HTTPException(status_code=503, detail="Visual generation failed (VRAM limit reached or SD error).")
        
    # Convert filenames to full URLs
    image_urls = [f"/static/images/{filename}" for filename in filenames]
    
    return VisualResponse(image_urls=image_urls)

@router.get("/file/{filename}")
def get_image_file(filename: str):
    """
    Serves the actual image file.
    """
    file_path = os.path.join(ABSOLUTE_IMAGE_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Image file not found.")
        
    return FileResponse(file_path, media_type="image/png")