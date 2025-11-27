import uuid
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.utils.parsing import extract_text_from_pdf
from app.utils.chunking import chunk_text
from app.models.catalog import Catalog
from app.models.content import BookContent
from app.models.chunk import Chunk
from app.utils.fingerprint import create_minhash
from app.utils.embeddings import get_embedding
from app.utils.vector_store import vector_store
from app.models.scene import Scene, Character         
from app.utils.scene_extraction import extract_scenes

router = APIRouter()

def process_chunks(db: Session, catalog_id: str, full_text: str):
    """
    Background task to:
    1. Split text into chunks
    2. Generate AI embeddings (Vectors)
    3. Save chunks to Postgres
    4. Save vectors to FAISS Index
    """
    # 1. Split the text
    text_chunks = chunk_text(full_text, chunk_size=1000, overlap=100)
    print(f"Split into {len(text_chunks)} chunks. Generating embeddings...")
    
    chunk_objects = []
    vectors = []
    chunk_ids = []

    for i, content in enumerate(text_chunks):
        # Generate ID explicitly so we can send it to both DB and FAISS
        c_id = str(uuid.uuid4())

        # Create DB Object
        chunk_obj = Chunk(
            id=c_id,
            catalog_id=catalog_id,
            content=content,
            chunk_index=i
        )
        
        # Calculate Vector (The AI Part)
        # This converts text -> list of 384 numbers
        vec = get_embedding(content)
        
        chunk_objects.append(chunk_obj)
        vectors.append(vec)
        chunk_ids.append(c_id)
    
    # 2. Save Chunks to Postgres
    db.add_all(chunk_objects)
    db.commit()
    
    # 3. Save Vectors to FAISS
    # This makes the chunks "searchable" by meaning
    vector_store.add_vectors(vectors, chunk_ids)

    # 2. --- NEW: SCENE GRAPH EXTRACTION ---
    print("🎬 Extracting Scene Graph...")
    graph_data = extract_scenes(full_text)
    
    # Save Characters
    for name in graph_data["characters"]:
        # Only add unique names
        exists = db.query(Character).filter(Character.catalog_id == catalog_id, Character.name == name).first()
        if not exists:
            char_obj = Character(catalog_id=catalog_id, name=name)
            db.add(char_obj)
            
    # Save Scenes
    for scene_data in graph_data["scenes"]:
        scene_obj = Scene(
            catalog_id=catalog_id,
            order_index=scene_data["index"],
            title=scene_data["title"],
            content_summary=scene_data["content"],
            characters_present=scene_data["characters"],
            dialogues=scene_data["dialogues"]
        )
        db.add(scene_obj)
    db.commit()
    print(f"✅ Extracted {len(graph_data['scenes'])} scenes and {len(graph_data['characters'])} characters.")
    print(f"✅ Automatically created {len(text_chunks)} chunks + embeddings for book {catalog_id}")

@router.post("/upload")
async def upload_book(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...), 
    title: str = "", 
    author: str = "Unknown",
    db: Session = Depends(get_db)
):
    # FIX: Check if filename exists AND if it ends with .pdf (Satisfies Pylance)
    if not file.filename or not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files allowed for now.")
    
    file_content = await file.read()
    
    try:
        data = extract_text_from_pdf(file_content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF Parsing failed: {str(e)}")
    
    # Calculate Fingerprint (Digital ID)
    sample_text = data["full_text"][:5000] 
    signature = create_minhash(sample_text)

    final_title = title if title else file.filename
    
    # Create Catalog Entry
    new_book = Catalog(
        title=final_title, 
        author=author, 
        page_count=data["page_count"], 
        fingerprints=signature
    )
    db.add(new_book)
    db.commit()
    db.refresh(new_book)
    
    # Save Content (Full Text)
    content = BookContent(
        catalog_id=new_book.id,
        full_text=data["full_text"],
        filename=file.filename,
        file_size_bytes=len(file_content)
    )
    db.add(content)
    db.commit()
    
    # TRIGGER CHUNKING + EMBEDDING (Background Task)
    # Wraps ID in str() to satisfy type checkers
    background_tasks.add_task(process_chunks, db, str(new_book.id), data["full_text"])
    
    return {
        "status": "success",
        "book_id": new_book.id,
        "message": "Book ingested! Chunking and Embedding started in background."
    }