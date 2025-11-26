from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from dotenv import load_dotenv

# Load settings from .env
load_dotenv()

# 1. Get the Database URL
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

# 2. VALIDATION FIX: Ensure it is not None
if SQLALCHEMY_DATABASE_URL is None:
    raise ValueError("DATABASE_URL is not set. Please check your backend/.env file.")

# 3. Create the engine (Now safe because we know it's a string)
engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()