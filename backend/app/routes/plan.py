from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.scene import Scene
from app.utils.planner import generate_plan
from app import schemas
from typing import List

router = APIRouter()

# FIX: Added response_model=List[schemas.Scene]
@router.get("/list/{catalog_id}", response_model=List[schemas.Scene])
def list_scenes(catalog_id: str, db: Session = Depends(get_db)):
    """
    Helper to see available scenes for a book.
    Now properly formatted so you can see the IDs!
    """
    return db.query(Scene).filter(Scene.catalog_id == catalog_id).order_by(Scene.order_index).all()

@router.post("/{scene_id}", response_model=schemas.LessonPlan)
def create_lesson_plan(scene_id: str, db: Session = Depends(get_db)):
    """
    Generates a teaching plan for a specific Scene.
    """
    scene = db.query(Scene).filter(Scene.id == scene_id).first()
    if not scene:
        raise HTTPException(status_code=404, detail="Scene not found")

    chars = scene.characters_present if scene.characters_present else [] # type: ignore
    
    plan = generate_plan(
        scene_title=str(scene.title),
        characters=chars, # type: ignore
        content_summary=str(scene.content_summary)
    )
    
    plan.scene_id = str(scene.id)
    return plan