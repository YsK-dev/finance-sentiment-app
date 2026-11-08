from fastapi import APIRouter, HTTPException

from app.services.data_collector import data_collector

router = APIRouter()


@router.get("/news/{symbol}")
async def get_news_articles(symbol: str):
    """The articles collected for a symbol (an empty list when no source answers)."""
    try:
        symbol = symbol.upper()
        return {"symbol": symbol, "articles": await data_collector.get_news_articles(symbol)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch news: {e}")


@router.get("/feeds/{symbol}")
async def get_feed_posts(symbol: str):
    """Posts from general market news feeds that name the symbol."""
    try:
        symbol = symbol.upper()
        return {"symbol": symbol, "posts": await data_collector.get_feed_posts(symbol)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch feed posts: {e}")
