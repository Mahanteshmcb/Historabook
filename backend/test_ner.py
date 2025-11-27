from app.utils.ner import extract_entities

text = "Leonardo da Vinci lived in Florence. He met Niccolo Machiavelli near the Arno River."

print("Analyzing text...")
entities = extract_entities(text)

print(f"Found Characters: {entities['characters']}")
print(f"Found Locations: {entities['locations']}")

if "Florence" in entities['locations']:
    print("✅ NER is working!")
else:
    print("❌ Something went wrong.")