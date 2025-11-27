# Historabook: Interactive Multimodal Teaching Assistant

**Historabook** is an open-source, offline-capable AI teaching assistant. It ingests books/documents, understands their content, and teaches them to the user via interactive voice narration, real-time visuals, and structured pedagogy.

## 🚀 Current Status (Day 2 Complete)
- **Infrastructure:** Dockerized Postgres (Database) and Redis (Cache).
- **Backend:** FastAPI server initialized with SQLAlchemy ORM.
- **Database:** Connection established; `Catalog` model created.

---

## 🛠️ Tech Stack
- **Language:** Python 3.11+
- **API Framework:** FastAPI
- **Database:** PostgreSQL 15 (via Docker)
- **Caching:** Redis 7 (via Docker)
- **ORM:** SQLAlchemy
- **Server:** Uvicorn

---

## ⚡ Quick Start (Windows)

### 1. Prerequisites
- Docker Desktop (Running)
- Python 3.10+ (or Anaconda)

### 2. Setup Environment
1. Clone the repo and enter the directory:
   ```powershell
   cd Historabook

## Start the Infrastructure (Database & Cache):
docker compose up -d

## Configure Environment Variables:
Create a .env file in backend/ with the following:
PROJECT_NAME="Historabook"
POSTGRES_USER=postgres
POSTGRES_PASSWORD=changeme
POSTGRES_SERVER=localhost
POSTGRES_PORT=5432
POSTGRES_DB=historabook_db
DATABASE_URL=postgresql://postgres:changeme@localhost/historabook_db

## . Run the Server
Navigate to the backend folder and start the server:
cd backend
### Using standard Python
python -m uvicorn app.main:app --reload --port 8001

### OR if using Anaconda path directly:
& C:/ProgramData/anaconda3/python.exe -m uvicorn app.main:app --reload --port 8001


catalog_id : 46919a93-ffe0-4aad-b928-0d598b86cfb2