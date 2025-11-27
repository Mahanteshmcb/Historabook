from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.utils.embeddings import get_embedding
from app.utils.vector_store import vector_store
from app.models.chunk import Chunk
from app import schemas
from typing import List

router = APIRouter()

@router.get("/", response_model=schemas.SearchResponse)
def search_knowledge_base(
    query: str, 
    k: int = 5, 
    db: Session = Depends(get_db)
):
    """
    Semantic Search:
    1. Embeds the user query.
    2. Searches FAISS for the nearest chunks.
    3. Fetches the actual text content from Postgres.
    """
    if not query:
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    # 1. Convert Query to Vector
    query_vector = get_embedding(query)
    
    # 2. Search Vector Store
    # Returns list of tuples: (chunk_id, distance_score)
    search_results = vector_store.search(query_vector, k=k)
    
    if not search_results:
        return {"results": []}

    # Unpack IDs to fetch from DB
    found_ids = [res[0] for res in search_results]
    id_to_score = {res[0]: res[1] for res in search_results}

    # 3. Fetch Content from DB
    # We fetch only the chunks that FAISS found
    chunks = db.query(Chunk).filter(Chunk.id.in_(found_ids)).all()

    # 4. Format Response
    # We cast to str() to make Pylance happy
    results = []
    for chunk in chunks:
        c_id = str(chunk.id)
        
        results.append(schemas.SearchResult(
            chunk_id=c_id,
            content=str(chunk.content),
            page_number=chunk.page_number, # type: ignore
            score=id_to_score.get(c_id, 0.0)
        ))
    
    # Sort by score (lower is better distance, but typically we want closest match first)
    # Since FAISS returns distances, we just keep the list order or sort by score ascending
    results.sort(key=lambda x: x.score)

    return {"results": results}