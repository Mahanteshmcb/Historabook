from pydantic import BaseModel
from typing import Optional, List, Any

# --- 1. Catalog Schemas ---
class CatalogBase(BaseModel):
    title: str
    author: str
    synopsis: Optional[str] = None
    page_count: int = 0
    is_public: bool = True

class CatalogCreate(CatalogBase):
    pass

class Catalog(CatalogBase):
    id: str
    fingerprints: Optional[List[int]] = None

    class Config:
        from_attributes = True

# --- 2. Search & Resolve ---
class ResolveResult(BaseModel):
    results: List[Catalog]
    match_confidence: float

class SearchResult(BaseModel):
    chunk_id: str
    content: str
    page_number: Optional[int] = None
    score: float

class SearchResponse(BaseModel):
    results: List[SearchResult]

# --- 3. Scene Schemas ---
class Scene(BaseModel):
    id: str
    catalog_id: str
    order_index: int
    title: str
    content_summary: Optional[str] = None
    characters_present: Optional[List[str]] = []
    
    class Config:
        from_attributes = True

# --- 4. Planner Schemas (FIXED for Day 35) ---
# Renamed to match app/utils/planner.py expectations

class VisualPrompt(BaseModel):
    background: str
    camera_action: str = "static"

class Segment(BaseModel):
    text: str
    visual: VisualPrompt
    checkpoint_question: Optional[str] = ""

class LessonPlan(BaseModel):
    segments: List[Segment]
    scene_id: str