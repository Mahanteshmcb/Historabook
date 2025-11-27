from sqlalchemy import Column, String, Integer, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.db.session import Base
import uuid

def generate_uuid():
    return str(uuid.uuid4())

class Scene(Base):
    """A specific timeframe/location in the book (Day 14)"""
    __tablename__ = "scenes"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    catalog_id = Column(String, ForeignKey("catalog.id"))
    
    order_index = Column(Integer)  # 1st scene, 2nd scene...
    title = Column(String)         # e.g., "Chapter 1: The Beginning"
    content_summary = Column(Text) # Short explanation of what happens
    
    # Store list of character names present in this scene
    characters_present = Column(JSON) 
    
    # Store list of dialogue objects: [{"speaker": "Leo", "text": "Hello"}]
    dialogues = Column(JSON)      

class Character(Base):
    """Profile of a person found in the book (Day 11 & 12)"""
    __tablename__ = "characters"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    catalog_id = Column(String, ForeignKey("catalog.id"))
    
    name = Column(String)  # "Leonardo da Vinci"
    aliases = Column(JSON) # ["Leonardo", "da Vinci", "The Artist"]
    
    # We will use this later for Voice Cloning (Day 27)
    voice_profile_id = Column(String, nullable=True)