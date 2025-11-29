import os
import requests
from fastapi import FastAPI, Depends, UploadFile, File, HTTPException, Form
from pydantic import BaseModel
import shutil
import fitz # PyMuPDF
import math

from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.db.session import engine, Base, get_db

# Import Models
from app.models import catalog, content
from app.models.scene import Scene

# Import Routes
from app.routes import catalog as catalog_router
from app.routes import ingest as ingest_router
from app.routes import search as search_router
from app.routes import plan as plan_router
from app.routes import audio as audio_router
from app.routes import listen as listen_router
from app.routes import chat as chat_router
from app.routes import visuals as visuals_router

# --- CONFIG: PATHS ---
CURRENT_FILE = os.path.abspath(__file__)
APP_DIR = os.path.dirname(CURRENT_FILE)
BACKEND_DIR = os.path.dirname(APP_DIR)
STATIC_DIR = os.path.join(BACKEND_DIR, "static")

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Historabook AI", version="0.6.0")

# CORS
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- MOUNT STATIC FILES ---
os.makedirs(os.path.join(STATIC_DIR, "audio"), exist_ok=True)
if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# --- ROUTES ---
app.include_router(catalog_router.router, prefix="/api/catalog", tags=["Catalog"])
app.include_router(ingest_router.router, prefix="/api/ingest", tags=["Ingestion"])
app.include_router(search_router.router, prefix="/api/search", tags=["Search"])
app.include_router(plan_router.router, prefix="/api/plan", tags=["Planner"])
app.include_router(audio_router.router, prefix="/api/audio", tags=["Audio"])
app.include_router(listen_router.router, prefix="/api/listen", tags=["Listen"])
app.include_router(chat_router.router, prefix="/api/chat", tags=["Chat"])
app.include_router(visuals_router.router, prefix="/api/visuals", tags=["Visuals"])

@app.get("/")
async def root():
    index_path = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"error": "Frontend not found", "expected_path": index_path}

# --- UPLOAD ENDPOINT (3 MODES) ---
@app.post("/api/catalog/upload")
async def upload_book(
    file: UploadFile = File(...), 
    mode: str = Form("movie"), # trailer, movie, series
    db: Session = Depends(get_db)
):
    try:
        if not file.filename:
            raise HTTPException(status_code=400, detail="Filename is missing")
        
        filename = str(file.filename)
        os.makedirs("storage", exist_ok=True)
        file_path = f"storage/{filename}"
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        file_size = os.path.getsize(file_path)
        
        # Extract Text
        doc = fitz.open(file_path)
        full_text = ""
        # Read more pages for Series mode to get every detail
        page_limit = 200 if mode == "series" else 50 
        for i in range(len(doc)):
            if i > page_limit: break 
            page = doc[i]
            text = page.get_text()
            if text: full_text += str(text)
            
        book_id = filename.replace(".pdf", "").replace(" ", "_").lower()
        
        # Save Metadata
        new_book = catalog.Catalog(
            id=book_id,
            title=filename.replace(".pdf", ""),
            author="Unknown",
            synopsis=f"Mode: {mode.upper()} | " + full_text[:200] + "...", 
            is_public=True
        )
        db.merge(new_book)
        
        # Save Content
        existing_content = db.query(content.BookContent).filter(content.BookContent.catalog_id == book_id).first()
        if existing_content:
            existing_content.full_text = full_text # type: ignore
            existing_content.filename = filename # type: ignore
        else:
            new_content = content.BookContent(
                catalog_id=book_id, full_text=full_text, filename=filename, file_size_bytes=file_size
            )
            db.add(new_content)

        # --- SMART SLICING ---
        db.query(Scene).filter(Scene.catalog_id == book_id).delete()
        db.commit()

        if full_text:
            # MODE LOGIC
            if mode == "series":
                CHUNK_SIZE = 600  # ~1 min per scene. Highly detailed.
            elif mode == "movie":
                CHUNK_SIZE = 1500 # ~3 mins per scene. Balanced.
            else:
                CHUNK_SIZE = 4000 # ~8 mins per scene. Quick Summary.

            total_chars = len(full_text)
            num_scenes = math.ceil(total_chars / CHUNK_SIZE)
            
            print(f"📖 Slicing into {num_scenes} scenes (Mode: {mode})...")

            for i in range(num_scenes):
                start = i * CHUNK_SIZE
                end = min(start + CHUNK_SIZE, total_chars)
                chunk_text = full_text[start:end]
                
                if len(chunk_text.strip()) < 50: continue

                scene_title = f"Scene {i+1}"
                if i == 0: scene_title = "Chapter 1: The Beginning"
                elif i == num_scenes - 1: scene_title = "Final Chapter: Conclusion"

                new_scene = Scene(
                    id=f"{book_id}_s{i+1}",
                    catalog_id=book_id,
                    order_index=i,
                    title=scene_title,
                    content_summary=chunk_text,
                    characters_present=[]
                )
                db.add(new_scene)

        db.commit()
        
        return {"status": "success", "id": book_id, "title": new_book.title}

    except Exception as e:
        print(f"Upload Error: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

# --- CHAT & QUIZ ---
class QuizSubmission(BaseModel):
    question: str
    user_answer: str
    context: str = ""

@app.post("/api/quiz/evaluate")
async def evaluate_quiz(sub: QuizSubmission):
    try:
        resp = requests.post("http://localhost:11434/api/generate", json={
            "model": "mistral", 
            "prompt": f"Context: {sub.context}\nQ: {sub.question}\nA: {sub.user_answer}\nTask: Grade.", 
            "stream": False
        })
        return {"feedback": resp.json().get("response", "Error") if resp.status_code==200 else "AI Error"}
    except Exception as e: return {"feedback": str(e)}