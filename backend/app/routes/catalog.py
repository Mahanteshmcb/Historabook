from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app import schemas, crud

router = APIRouter()

@router.post("/", response_model=schemas.Catalog)
def create_book_entry(book: schemas.CatalogCreate, db: Session = Depends(get_db)):
    """Add a new book to the catalog manually."""
    return crud.create_book(db=db, book=book)

@router.get("/resolve", response_model=schemas.ResolveResult)
def resolve_book(query: str, db: Session = Depends(get_db)):
    """
    Search for a book by title.
    Example: GET /resolve?query=Harry
    """
    matches = crud.get_book_by_title(db, title=query)
    
    # Simple confidence logic for now (1.0 if exact match found, else 0.0)
    confidence = 1.0 if matches else 0.0
    
    return {"results": matches, "match_confidence": confidence}

@router.get("/", response_model=List[schemas.Catalog])
def read_catalog(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """List all books in the catalog."""
    return crud.get_all_books(db, skip=skip, limit=limit)