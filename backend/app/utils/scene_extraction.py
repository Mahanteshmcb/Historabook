import spacy
import re
from collections import Counter

# Load spaCy
try:
    nlp = spacy.load("en_core_web_sm")
except:
    nlp = spacy.blank("en") 

def extract_scenes(full_text: str):
    """
    Main pipeline to convert text into Scenes, Characters, and Dialogue.
    High-Granularity Version: Splits by paragraphs/double-newlines.
    """
    # Limit text size for MVP speed (increase this if you want more of the book processed)
    # 300,000 chars is roughly 100 pages. For the full 500 pages, you might need 1,000,000+
    # taking longer to process.
    doc = nlp(full_text[:300000]) 

    # --- 1. Entity Extraction ---
    people = [ent.text for ent in doc.ents if ent.label_ == "PERSON"]
    character_counts = Counter(people)
    top_characters = [name for name, count in character_counts.most_common(20)]

    # --- 2. Dialogue Detection ---
    dialogue_pattern = re.compile(r'“([^”]+)”|"([^"]+)"')
    all_quotes = dialogue_pattern.findall(full_text)
    clean_quotes = [q[0] or q[1] for q in all_quotes if q[0] or q[1]]

    # --- 3. Scene Boundary Detection (High Granularity) ---
    # Split by double newlines (paragraphs)
    raw_scenes = re.split(r'\n\s*\n', full_text)
    
    structured_scenes = []
    current_index = 0
    
    for segment in raw_scenes:
        # Skip only very short noise/headers (less than 50 chars)
        if len(segment) < 50: 
            continue
        
        # Check who is in this segment
        chars_in_scene = [name for name in top_characters if name in segment]
        
        # Check for dialogue
        scene_quotes = []
        for quote in clean_quotes:
            if quote in segment:
                scene_quotes.append({"text": quote, "speaker": "Unknown"})

        structured_scenes.append({
            "index": current_index,
            "title": f"Scene {current_index + 1}",
            "content": segment[:500] + "...", # Summary for DB (first 500 chars)
            "characters": list(set(chars_in_scene)),
            "dialogues": scene_quotes
        })
        current_index += 1

    return {
        "characters": top_characters,
        "scenes": structured_scenes
    }