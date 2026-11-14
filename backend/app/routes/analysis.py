from fastapi import APIRouter, HTTPException

from app.models.schemas import AnalysisResult
from app.services.analysis_engine import NoNewsFound, analysis_engine

router = APIRouter()


@router.get("/symbol/{symbol}", response_model=AnalysisResult)
async def analyze_symbol(symbol: str):
    """Label each recent headline about the symbol and combine the labels."""
    try:
        return await analysis_engine.analyze_symbol(symbol.upper())
    except NoNewsFound as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {e}")
