import os
from contextlib import asynccontextmanager
from pathlib import Path

from dotenv import load_dotenv

# Read backend/.env before the services are imported: they read their settings at import time.
load_dotenv()

import asyncio  # noqa: E402

from fastapi import FastAPI, HTTPException  # noqa: E402
from fastapi.middleware.cors import CORSMiddleware  # noqa: E402
from fastapi.responses import FileResponse  # noqa: E402

from app.routes import analysis, data, sentiment  # noqa: E402
from app.services.data_collector import data_collector  # noqa: E402
from app.services.sentiment_analyzer import sentiment_analyzer  # noqa: E402


@asynccontextmanager
async def lifespan(app: FastAPI):
    await asyncio.to_thread(sentiment_analyzer.load)  # load FinBERT once, before the first request
    yield
    await data_collector.close_session()


app = FastAPI(
    title="Finance Sentiment Analysis API",
    description="News sentiment for stock symbols, scored with FinBERT",
    version="2.0.0",
    lifespan=lifespan,
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


def add_frontend(app: FastAPI, static_dir: Path) -> None:
    """Serve the built React app: real files as they are, every other page path as index.html."""
    static_dir = static_dir.resolve()

    @app.api_route("/{path:path}", methods=["GET", "HEAD"], include_in_schema=False)
    async def frontend(path: str):
        if path.startswith("api/"):
            raise HTTPException(status_code=404, detail="Not found")
        file = (static_dir / path).resolve()
        if path and file.is_file() and file.is_relative_to(static_dir):
            return FileResponse(file)
        # Client-side routes (/youtube, ...) load index.html; React Router takes over.
        return FileResponse(static_dir / "index.html")


# The Docker image builds the frontend into STATIC_DIR; locally it is frontend/dist after `npm run build`.
STATIC_DIR = Path(os.getenv("STATIC_DIR", Path(__file__).resolve().parents[2] / "frontend" / "dist"))
if (STATIC_DIR / "index.html").exists():
    add_frontend(app, STATIC_DIR)
else:
    @app.get("/")
    async def root():
        return {"message": "Finance Sentiment Analysis API", "docs": "/docs"}
