import os
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.db.session import engine, Base, get_db
# Import Models (to create tables)
from app.models import catalog, content, chunk, scene
# Import Routes
from app.routes import catalog as catalog_router
from app.routes import ingest as ingest_router
from app.routes import search as search_router
from app.routes import plan as plan_router
from app.routes import audio as audio_router
from app.routes import listen as listen_router
from app.routes import chat as chat_router

# --- CONFIG: PATHS ---
CURRENT_FILE = os.path.abspath(__file__)
APP_DIR = os.path.dirname(CURRENT_FILE)
BACKEND_DIR = os.path.dirname(APP_DIR)
STATIC_DIR = os.path.join(BACKEND_DIR, "static")

# Create tables (Runs on startup)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Historabook AI", version="0.4.0")

# CORS Setup (Allows all ports on localhost, plus dynamic origin check)
origins = ["http://localhost:3000", "http://localhost:5173", "http://localhost:8001", "http://127.0.0.1:8001"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow all origins for local testing simplicity
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- MOUNT STATIC FILES ---
# Ensure folder exists
os.makedirs(os.path.join(STATIC_DIR, "audio"), exist_ok=True)

# Mount /static endpoint for audio/assets
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

# --- HOMEPAGE (THE PLAYER) ---
@app.get("/")
async def root():
    # Serves the index.html file
    index_path = os.path.join(STATIC_DIR, "index.html")
    
    if os.path.exists(index_path):
        return FileResponse(index_path)
    
    return {"error": "Frontend not found", "expected_path": index_path}

# Debug Endpoint (for quick checks)
@app.get("/debug/stats")
def get_stats(db: Session = Depends(get_db)):
    # Requires existing models (catalog, chunk, scene)
    book_count = db.query(catalog.Catalog).count()
    chunk_count = db.query(chunk.Chunk).count()
    scene_count = db.query(scene.Scene).count()
    return {
        "total_books": book_count,
        "total_chunks": chunk_count,
        "total_scenes": scene_count
    }