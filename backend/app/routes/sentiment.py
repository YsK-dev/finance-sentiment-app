from fastapi import APIRouter, HTTPException
from app.models.schemas import SentimentRequest, SentimentResponse, YouTubeTranscriptRequest
from app.services.sentiment_analyzer import sentiment_analyzer
from app.services.data_collector import data_collector

router = APIRouter()

@router.post("/analyze", response_model=SentimentResponse)
async def analyze_sentiment(request: SentimentRequest):
    """Analyze sentiment of financial text"""
    try:
        result = await sentiment_analyzer.analyze_sentiment(request.text)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sentiment analysis failed: {str(e)}")

@router.post("/youtube/transcript")
async def get_youtube_sentiment(request: YouTubeTranscriptRequest):
    """Get and analyze YouTube video transcript"""
    try:
        # Get transcript
        transcript = await data_collector.get_youtube_transcript(
            request.video_id, 
            request.language
        )
        
        if not transcript:
            raise HTTPException(
                status_code=404, 
                detail=f"Transcript not available for video {request.video_id} in language '{request.language}'. The video may not have captions, or captions may only be available in other languages."
            )
        
        # Analyze sentiment
        sentiment_result = await sentiment_analyzer.analyze_sentiment(transcript)
        
        return {
            "video_id": request.video_id,
            "transcript_preview": transcript[:200] + "..." if len(transcript) > 200 else transcript,
            "sentiment": sentiment_result.dict()
        }
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"YouTube analysis failed: {str(e)}"
        )

@router.post("/batch")
async def analyze_batch_sentiment(texts: list):
    """Analyze sentiment for multiple texts"""
    try:
        results = await sentiment_analyzer.analyze_batch(texts)
        return {"results": [result.dict() for result in results]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch analysis failed: {str(e)}")
