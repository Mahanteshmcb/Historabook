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

# --- 2. Resolve Schemas (RESTORED) ---
class ResolveResult(BaseModel):
    results: List[Catalog]
    match_confidence: float

# --- 3. Search Schemas ---
class SearchResult(BaseModel):
    chunk_id: str
    content: str
    page_number: Optional[int] = None
    score: float

class SearchResponse(BaseModel):
    results: List[SearchResult]

# --- 4. Scene Schemas ---
class Scene(BaseModel):
    id: str
    catalog_id: str
    order_index: int
    title: str
    content_summary: Optional[str] = None
    characters_present: Optional[List[str]] = []
    
    class Config:
        from_attributes = True

# --- 5. Planner Schemas ---
class VisualSpec(BaseModel):
    character_focus: Optional[str] = None
    background: str = "default_classroom"
    camera_action: str = "static"
    style: str = "realistic"

class NarrationSegment(BaseModel):
    index: int
    text: str
    visual: VisualSpec
    analogy: Optional[str] = None
    checkpoint_question: Optional[str] = None
    
class LessonPlan(BaseModel):
    scene_id: str
    segments: List[NarrationSegment]