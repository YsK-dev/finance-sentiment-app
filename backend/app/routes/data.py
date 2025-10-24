from fastapi import APIRouter, HTTPException
from app.services.data_collector import data_collector

router = APIRouter()

@router.get("/news/{symbol}")
async def get_news_articles(symbol: str):
    """Get news articles for a symbol"""
    try:
        articles = await data_collector.get_news_articles(symbol)
        return {"symbol": symbol, "articles": articles}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch news: {str(e)}")

@router.get("/blogs/{symbol}")
async def get_blog_posts(symbol: str):
    """Get blog posts for a symbol"""
    try:
        posts = await data_collector.get_blog_posts(symbol)
        return {"symbol": symbol, "posts": posts}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch blog posts: {str(e)}")
