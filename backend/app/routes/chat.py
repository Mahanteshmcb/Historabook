from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.utils.vector_store import vector_store
from app.utils.embeddings import get_embedding
from app.utils.llm import get_model
from app.utils.tts_piper import generate_audio
from app.models.chunk import Chunk

router = APIRouter()

class ChatRequest(BaseModel):
    question: str
    catalog_id: str

@router.post("/reply")
def reply_to_user(req: ChatRequest, db: Session = Depends(get_db)):
    """
    Full RAG Pipeline:
    Question -> Vector Search -> DB Context -> LLM Answer -> TTS Audio
    """
    print(f"🗣️ User asked: {req.question}")

    # 1. SEARCH (Retrieve Context)
    query_vector = get_embedding(req.question)
    search_results = vector_store.search(query_vector, k=3)
    
    context_text = ""
    if search_results:
        found_ids = [res[0] for res in search_results]
        # Fetch text from Postgres
        chunks = db.query(Chunk).filter(Chunk.id.in_(found_ids)).all()
        
        # FIX: Pylance fix (ensure contents are strings)
        context_text = "\n\n".join([str(c.content) for c in chunks])
        
        print(f"📚 Found {len(chunks)} relevant facts.")
    
    # 2. THINK (Ask LLM)
    llm = get_model()
    
    prompt = f"""<|system|>
You are a helpful assistant teaching a book. Use the Context below to answer the user. Keep it short (2 sentences max).
<|end|>
<|user|>
Context: {context_text}

Question: {req.question}
<|end|>
<|assistant|>"""

    output = llm(
        prompt, 
        max_tokens=100,
        stop=["<|end|>"],
        echo=False,
        stream=False
    )
    
    # FIX: Type ignore for Pylance Stream error
    answer_text = output["choices"][0]["text"].strip() # type: ignore
    print(f"🤖 AI Answer: {answer_text}")

    # 3. SPEAK (Generate Audio)
    audio_filename = generate_audio(answer_text, lang="en")
    
    return {
        "text": answer_text,
        "audio_url": f"/api/audio/file/{audio_filename}"
    }