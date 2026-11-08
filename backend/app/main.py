import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.routes import analysis, data, sentiment

load_dotenv()

app = FastAPI(
    title="Finance Sentiment Analysis API",
    description="News sentiment for stock symbols, scored with FinBERT",
    version="2.0.0",
)

# The Vite dev server runs on another port; in the single-container build the
# frontend is served by this app, so no CORS is needed there.
allowed_origins = ["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:5173", "http://127.0.0.1:5173"]
if os.getenv("FRONTEND_URL"):
    allowed_origins.append(os.environ["FRONTEND_URL"])
app.add_middleware(CORSMiddleware, allow_origins=allowed_origins, allow_methods=["*"], allow_headers=["*"])

app.include_router(sentiment.router, prefix="/api/sentiment", tags=["sentiment"])
app.include_router(analysis.router, prefix="/api/analysis", tags=["analysis"])
app.include_router(data.router, prefix="/api/data", tags=["data"])


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "finance-sentiment-api"}


# Serve the built React app when it is present (the Docker image builds it into STATIC_DIR).
STATIC_DIR = Path(os.getenv("STATIC_DIR", Path(__file__).resolve().parents[2] / "frontend" / "dist"))
if (STATIC_DIR / "index.html").exists():
    app.mount("/assets", StaticFiles(directory=STATIC_DIR / "assets"), name="assets")

    @app.get("/{path:path}", include_in_schema=False)
    async def spa(path: str):
        # Client-side routes (/youtube, ...) all load index.html; React Router takes over.
        if path.startswith("api/"):
            raise HTTPException(status_code=404, detail="Not found")
        return FileResponse(STATIC_DIR / "index.html")
else:
    @app.get("/")
    async def root():
        return {"message": "Finance Sentiment Analysis API", "docs": "/docs"}
