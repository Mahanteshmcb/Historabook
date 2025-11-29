from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.scene import Scene
from app.utils.planner import generate_plan # Imports logic from utils
from app import schemas
from typing import List
from app.utils.visual_engine import ABSOLUTE_IMAGE_DIR
import os

# This is the variable main.py is looking for!
router = APIRouter()

@router.get("/list/{catalog_id}", response_model=List[schemas.Scene])
def list_scenes(catalog_id: str, db: Session = Depends(get_db)):
    """
    List all scenes for a specific book.
    """
    return db.query(Scene).filter(Scene.catalog_id == catalog_id).order_by(Scene.order_index).all()

@router.post("/{scene_id}", response_model=schemas.LessonPlan)
def create_lesson_plan(scene_id: str, db: Session = Depends(get_db)):
    """
    Generate a lesson plan for a scene using the logic in utils/planner.py
    """
    scene = db.query(Scene).filter(Scene.id == scene_id).first()
    if not scene:
        raise HTTPException(status_code=404, detail="Scene not found")

    # Pass data to the utility function
    chars = scene.characters_present if scene.characters_present else [] # type: ignore
    
    plan = generate_plan(
        scene_title=str(scene.title),
        characters=chars, # type: ignore
        content_summary=str(scene.content_summary)
    )
    
    plan.scene_id = str(scene.id)
    return plan

@router.get("/status/{scene_id}")
def check_scene_status(scene_id: str):
    """
    Checks if audio and visual files already exist for this scene.
    Used by frontend to skip re-generation.
    """
    # We need to guess the filenames based on how they are generated.
    # Since our current generator uses random UUIDs, we can't easily guess filenames without a database.
    # 
    # FIX: We need to store generated filenames in the DB to make this work perfectly.
    # FOR NOW (MVP): We will return "not ready" to be safe, 
    # OR we rely on the frontend's 'sceneCache' which is lost on refresh.
    
    # REAL FIX: The backend needs to remember which scenes are done.
    # Let's assume if the Plan exists, it might be done.
    
    # ... Actually, without DB storage for file paths, we can't know for sure.
    # But we can rely on the existing "generate" endpoint returning 200 OK quickly.
    
    return {"ready": False}