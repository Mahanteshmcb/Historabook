import requests
from app.schemas import LessonPlan, Segment, VisualPrompt

# --- OPTIMIZED PROMPT (No Quiz) ---
PROMPT_TEMPLATE = """
You are an expert educational content creator.
Analyze the following text from a book regarding "{scene_title}".

TEXT CONTENT:
{content_summary}

TASK:
Create a short, engaging educational script.
1. NARRATION: Write a 1-2 sentence script for a narrator explaining the key concept.
2. VISUAL: Describe a highly detailed, cinematic image to accompany this narration. Focus on lighting, setting, and objects.

FORMAT:
NARRATION: (Text)
VISUAL: (Description)
"""

def generate_plan(scene_title: str, characters: list, content_summary: str) -> LessonPlan:
    """
    Generates a Lesson Plan using local Ollama (Mistral/Llama).
    Optimized for Day 35: No Quizzes, faster generation.
    """
    
    # 1. Prepare Prompt
    # Truncate content to 2000 chars to prevent context overflow and speed up
    prompt = PROMPT_TEMPLATE.format(
        scene_title=scene_title,
        content_summary=content_summary[:2000] 
    )

    print(f"🤖 Planning lesson for: {scene_title}...")

    # 2. Call Ollama
    try:
        response = requests.post("http://localhost:11434/api/generate", json={
            "model": "mistral", # Ensure this matches your installed model
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.7, 
                "num_ctx": 4096
            }
        })
        
        if response.status_code != 200:
            print(f"❌ Ollama Error: {response.text}")
            return LessonPlan(segments=[], scene_id="error")
            
        ai_output = response.json().get("response", "")
        
        # 3. Parse Response (NARRATION -> VISUAL)
        segments = []
        
        # Split by "NARRATION:" key to find blocks
        raw_blocks = ai_output.split("NARRATION:")
        
        for block in raw_blocks:
            if not block.strip(): continue
            
            narration_text = ""
            visual_desc = ""
            
            # Extract VISUAL part
            if "VISUAL:" in block:
                subparts = block.split("VISUAL:")
                narration_text = subparts[0].strip()
                visual_desc = subparts[1].strip()
            else:
                # Fallback
                narration_text = block.strip()
                visual_desc = "A cinematic, detailed educational scene."

            if narration_text:
                # Create Segment Object using the CORRECT Schema names
                segments.append(Segment(
                    text=narration_text,
                    visual=VisualPrompt(
                        background=visual_desc + ", cinematic lighting, 8k, detailed, depth of field",
                        camera_action="subtle camera motion"
                    ),
                    checkpoint_question="" 
                ))

        return LessonPlan(segments=segments, scene_id="temp")

    except Exception as e:
        print(f"Planner Error: {e}")
        return LessonPlan(segments=[], scene_id="error")