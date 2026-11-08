from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class SentimentLabel(str, Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"


class SentimentRequest(BaseModel):
    text: str = Field(..., min_length=1, description="Text to analyze")


class SentimentResponse(BaseModel):
    sentiment: SentimentLabel
    confidence: float = Field(..., ge=0.0, le=1.0, description="Model score for the label (not a calibrated probability)")
    raw_scores: Dict[str, float]
    model: str = Field(..., description="Which model produced the label: finbert or keywords")
    chunks: Optional[int] = Field(None, description="For long texts: how many pieces were scored and averaged")


class YouTubeTranscriptRequest(BaseModel):
    video_id: str = Field(..., description="YouTube video ID")
    language: str = Field(default="en", description="Transcript language code")


class ScoredArticle(BaseModel):
    title: str
    url: str
    source: str
    published: str
    sentiment: SentimentLabel
    score: float = Field(..., description="Model score for this headline's label")


class AnalysisResult(BaseModel):
    symbol: str
    overall_sentiment: SentimentLabel = Field(..., description="The most common label among the headlines")
    agreement: float = Field(..., ge=0.0, le=1.0, description="Share of headlines with the overall label")
    label_counts: Dict[str, int]
    rule_label: str = Field(..., description="BUY, HOLD or SELL: positive, neutral or negative overall")
    model: str
    articles: List[ScoredArticle]
    timestamp: datetime
