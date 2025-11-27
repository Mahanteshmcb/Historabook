from sqlalchemy.orm import Session
from app.models import catalog as models
from app import schemas

def get_book_by_title(db: Session, title: str):
    # Simple case-insensitive search (ILIKE equivalent in python logic or SQL)
    return db.query(models.Catalog).filter(models.Catalog.title.ilike(f"%{title}%")).all()

def create_book(db: Session, book: schemas.CatalogCreate):
    db_book = models.Catalog(
        title=book.title,
        author=book.author,
        synopsis=book.synopsis,
        page_count=book.page_count
    )
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book

def get_all_books(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Catalog).offset(skip).limit(limit).all()