from app.db.session import SessionLocal
from app.models.catalog import Catalog
from app.models.scene import Scene

db = SessionLocal()

# 1. Get the most recent book uploaded
latest_book = db.query(Catalog).order_by(Catalog.id.desc()).first()

if not latest_book:
    print("❌ No books found in database!")
else:
    print(f"\n✅ FOUND BOOK: {latest_book.title}")
    print(f"   Catalog ID: {latest_book.id}")
    
    # 2. Get the first scene for this book
    first_scene = db.query(Scene).filter(Scene.catalog_id == latest_book.id).first()
    
    if first_scene:
        print(f"\n✅ FOUND SCENE 1")
        print(f"   Scene Title: {first_scene.title}")
        print(f"   Scene ID:    {first_scene.id}")  # <--- THIS IS WHAT YOU NEED
        print(f"\n👉 Next Step: Go to POST /api/plan/{first_scene.id}")
    else:
        print("\n❌ No scenes found for this book. (Did the extraction save?)")

db.close()