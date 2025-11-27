import spacy

# Load the model once
nlp = spacy.load("en_core_web_sm")

def extract_entities(text: str):
    """
    Analyzes text and returns unique Characters and Locations.
    """
    if not text:
        return {"characters": [], "locations": []}
        
    doc = nlp(text)
    
    characters = set()
    locations = set()
    
    for ent in doc.ents:
        # PERSON = People, Characters
        if ent.label_ == "PERSON":
            characters.add(ent.text)
        # GPE = Countries, Cities, States
        # LOC = Non-GPE locations, mountain ranges, bodies of water
        elif ent.label_ in ["GPE", "LOC"]:
            locations.add(ent.text)
            
    return {
        "characters": list(characters),
        "locations": list(locations)
    }