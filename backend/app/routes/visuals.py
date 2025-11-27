from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.utils.visual_engine import generate_visual_draft, ABSOLUTE_IMAGE_DIR
from fastapi.responses import FileResponse
from typing import List
import os

router = APIRouter()

class VisualRequest(BaseModel):
    prompt: str

class VisualResponse(BaseModel):
    # The API now returns a list of image URLs for the animation
    image_urls: List[str]

@router.post("/generate", response_model=VisualResponse)
def generate_draft(request: VisualRequest):
    """
    Receives a visual prompt, generates multiple frames, and returns a list of URLs.
    """
    if not request.prompt:
        raise HTTPException(status_code=400, detail="Prompt required.")

    # Get the list of filenames from the generation utility
    filenames = generate_visual_draft(request.prompt) 
    
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