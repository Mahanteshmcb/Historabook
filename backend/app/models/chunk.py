from sqlalchemy import Column, String, Text, Integer, ForeignKey
from app.db.session import Base
import uuid

def generate_uuid():
    return str(uuid.uuid4())

class Chunk(Base):
    __tablename__ = "chunks"

    id = Column(String, primary_key=True, default=generate_uuid, index=True)
    catalog_id = Column(String, ForeignKey("catalog.id"), index=True)
    
    content = Column(Text)       # The actual text snippet
    chunk_index = Column(Integer) # Order (0, 1, 2, 3...)
    
    # Metadata for citations
    page_number = Column(Integer, nullable=True) 
    
    # We will fill this in Day 9 (Embeddings)
    # embedding_id = Column(String, nullable=True)