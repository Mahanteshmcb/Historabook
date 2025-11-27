from sqlalchemy import Column, String, Text, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.db.session import Base
import uuid

def generate_uuid():
    return str(uuid.uuid4())

class BookContent(Base):
    __tablename__ = "book_content"

    id = Column(String, primary_key=True, default=generate_uuid, index=True)
    catalog_id = Column(String, ForeignKey("catalog.id"))
    
    # We store the full text here for the MVP (Simple & Fast)
    full_text = Column(Text)
    
    # Metadata
    filename = Column(String)
    file_size_bytes = Column(Integer)