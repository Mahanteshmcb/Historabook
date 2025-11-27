from sqlalchemy import Column, String, Integer, Text, Boolean, JSON  # <--- Added JSON
from app.db.session import Base
import uuid

def generate_uuid():
    return str(uuid.uuid4())

class Catalog(Base):
    __tablename__ = "catalog"

    id = Column(String, primary_key=True, default=generate_uuid, index=True)
    title = Column(String, index=True)
    author = Column(String, index=True)
    synopsis = Column(Text, nullable=True)
    page_count = Column(Integer, default=0)
    is_public = Column(Boolean, default=True)
    
    # NEW: Stores the MinHash signature
    fingerprints = Column(JSON, nullable=True)