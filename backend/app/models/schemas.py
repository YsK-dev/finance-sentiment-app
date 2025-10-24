from pydantic import BaseModel, Field
from enum import Enum
from typing import List, Dict, Optional, Any
from datetime import datetime


class SentimentLabel(str, Enum):
    """Sentiment classification labels"""
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"


class SourceType(str, Enum):
    """Data source types"""
    NEWS = "news"
    YOUTUBE = "youtube"
    BLOG = "blog"
    SOCIAL = "social"


class SentimentRequest(BaseModel):
    """Request model for sentiment analysis"""
    text: str = Field(..., min_length=1, description="Text to analyze")


class SentimentResponse(BaseModel):
    """Response model for sentiment analysis"""
    sentiment: SentimentLabel
    confidence: float = Field(..., ge=0.0, le=1.0)
    raw_scores: Dict[str, float]


class YouTubeTranscriptRequest(BaseModel):
    """Request model for YouTube transcript analysis"""
    video_id: str = Field(..., description="YouTube video ID")
    language: str = Field(default="en", description="Transcript language code")


class AnalysisResult(BaseModel):
    """Comprehensive analysis result"""
    symbol: str
    overall_sentiment: SentimentLabel
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    source_breakdown: Dict[str, float]
    recommendation: str
    risk_level: str
    key_insights: List[str]
    timestamp: datetime


class InvestmentAdvice(BaseModel):
    """Investment advice model"""
    symbol: str
    action: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    reasoning: List[str]
    time_horizon: str
    risk_factors: List[str]


class NewsRequest(BaseModel):
    """Request model for news analysis"""
    symbol: str
    days: int = Field(default=7, ge=1, le=30, description="Number of days to analyze")
