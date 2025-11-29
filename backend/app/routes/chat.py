from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel
from typing import List, Optional, Dict
import requests

router = APIRouter()

# --- IN-MEMORY HISTORY ---
# Stores the last 5 messages for every user session
chat_memory: Dict[str, List[dict]] = {}

class ChatRequest(BaseModel):
    question: str
    catalog_id: Optional[str] = None
    session_id: str = "default" # Frontend now sends this!

@router.post("/reply")
async def reply_to_chat(req: ChatRequest):
    """
    Smart Chat endpoint with Memory and Suggestions.
    """
    try:
        # 1. Retrieve History
        history = chat_memory.get(req.session_id, [])
        
        # Keep context tight (Last 3 turns)
        short_history = history[-6:] 
        
        history_str = ""
        for msg in short_history:
            history_str += f"{msg['role']}: {msg['content']}\n"

        # 2. Build Prompt with Memory
        prompt = f"""
        You are Historabook AI, a helpful and encouraging tutor.
        
        CONVERSATION HISTORY:
        {history_str}
        
        USER'S NEW QUESTION: "{req.question}"
        
        TASK:
        1. Answer the question clearly (max 2-3 sentences).
        2. Provide 3 short, curious follow-up questions the user might want to ask next.
        
        FORMAT OUTPUT EXACTLY LIKE THIS:
        [ANSWER]
        (Write answer here)
        
        [SUGGESTIONS]
        - (Follow up 1)
        - (Follow up 2)
        - (Follow up 3)
        """

        # 3. Call Ollama
        print(f"🧠 Thinking with {len(short_history)} context items...")
        resp = requests.post("http://localhost:11434/api/generate", json={
            "model": "mistral", # Make sure this matches your installed model
            "prompt": prompt,
            "stream": False
        })
        
        if resp.status_code != 200:
            return {"text": "My brain is offline.", "suggestions": []}

        full_output = resp.json().get("response", "")
        
        # 4. Parse Answer vs Suggestions
        answer_text = full_output
        suggestions = []
        
        if "[ANSWER]" in full_output:
            parts = full_output.split("[SUGGESTIONS]")
            answer_text = parts[0].replace("[ANSWER]", "").strip()
            
            if len(parts) > 1:
                lines = parts[1].strip().split("\n")
                for line in lines:
                    clean = line.strip().replace("- ", "").replace("* ", "")
                    if clean:
                        suggestions.append(clean)

        # 5. Save to Memory
        history.append({"role": "User", "content": req.question})
        history.append({"role": "AI", "content": answer_text})
        chat_memory[req.session_id] = history

        # 6. Return
        return {
            "text": answer_text,
            "suggestions": suggestions[:3],
            "audio_url": "" # We can add TTS here later if you want the chatbot to speak too!
        }

    except Exception as e:
        print(f"Chat Error: {e}")
        return {"text": f"Error: {str(e)}", "suggestions": []}