from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Initialize the API
app = FastAPI(
    title="Historabook API",
    description="Backend for Interactive Multimodal Teaching Assistant",
    version="0.1.0",
    docs_url="/docs",  # Swagger UI
    redoc_url="/redoc"
)

# Set up CORS (Cross-Origin Resource Sharing)
# This allows your frontend (React) to talk to this backend
origins = [
    "http://localhost:3000",  # React default port
    "http://localhost:5173",  # Vite default port
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Health check endpoint."""
    return {"message": "Historabook Backend is running!", "status": "active"}

@app.get("/api/health")
async def health_check():
    """Explicit health check for Docker/K8s."""
    return {"status": "healthy"}