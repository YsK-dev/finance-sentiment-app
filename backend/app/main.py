from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
import os

from app.routes import sentiment, analysis, data
from app.utils.database import connect_db, close_db

load_dotenv()

app = FastAPI(
    title="Finance Sentiment Analysis API",
    description="AI-powered investment advice using sentiment analysis",
    version="1.0.0"
)

# CORS middleware - Allow production and development origins
allowed_origins = [
    "http://localhost:3000", 
    "http://127.0.0.1:3000",
    "http://localhost:5173",  # Vite default port
    "http://127.0.0.1:5173",
    "https://finance-sentiment-app-1.onrender.com",  # Production frontend
]

# Also allow any Render domain for flexibility
frontend_url = os.getenv("FRONTEND_URL")
if frontend_url and frontend_url not in allowed_origins:
    allowed_origins.append(frontend_url)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
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
