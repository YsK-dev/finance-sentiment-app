import sys
import os
from pathlib import Path

# Add the backend directory to Python path for proper module resolution
# This should be /opt/render/project/src/backend on Render
backend_dir = Path(__file__).resolve().parent.parent
print(f"DEBUG: __file__ = {__file__}")
print(f"DEBUG: backend_dir = {backend_dir}")
print(f"DEBUG: backend_dir exists = {backend_dir.exists()}")
print(f"DEBUG: sys.path before = {sys.path[:3]}")

if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))
    print(f"DEBUG: Added {backend_dir} to sys.path")

print(f"DEBUG: sys.path after = {sys.path[:3]}")

# Check if app directory exists
app_dir = backend_dir / "app"
print(f"DEBUG: app_dir = {app_dir}")
print(f"DEBUG: app_dir exists = {app_dir.exists()}")
if app_dir.exists():
    print(f"DEBUG: app_dir contents = {list(app_dir.iterdir())}")

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

from app.routes import sentiment, analysis, data
from app.utils.database import connect_db, close_db

load_dotenv()

app = FastAPI(
    title="Finance Sentiment Analysis API",
    description="AI-powered investment advice using sentiment analysis",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000", 
        "http://127.0.0.1:3000",
        "http://localhost:5173",  # Vite default port
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database events
@app.on_event("startup")
async def startup_event():
    await connect_db()

@app.on_event("shutdown")
async def shutdown_event():
    await close_db()

# Routes
app.include_router(sentiment.router, prefix="/api/sentiment", tags=["sentiment"])
app.include_router(analysis.router, prefix="/api/analysis", tags=["analysis"])
app.include_router(data.router, prefix="/api/data", tags=["data"])

@app.get("/")
async def root():
    return {"message": "Finance Sentiment Analysis API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "finance-sentiment-api"}
