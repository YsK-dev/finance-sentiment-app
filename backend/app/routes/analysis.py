from fastapi import APIRouter, HTTPException
from app.models.schemas import AnalysisResult, InvestmentAdvice, NewsRequest
from app.services.analysis_engine import analysis_engine

router = APIRouter()

@router.get("/symbol/{symbol}", response_model=AnalysisResult)
async def analyze_symbol(symbol: str, days: int = 7):
    """Comprehensive analysis for a financial symbol"""
    try:
        result = await analysis_engine.analyze_symbol(symbol.upper(), days)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@router.get("/advice/{symbol}", response_model=InvestmentAdvice)
async def get_investment_advice(symbol: str):
    """Get long-term investment advice"""
    try:
        advice = await analysis_engine.get_investment_advice(symbol.upper())
        return advice
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Advice generation failed: {str(e)}")

@router.post("/news")
async def analyze_news_sentiment(request: NewsRequest):
    """Analyze news sentiment for a symbol"""
    try:
        # This would integrate with actual news APIs in production
        analysis = await analysis_engine.analyze_symbol(request.symbol, request.days)
        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"News analysis failed: {str(e)}")
