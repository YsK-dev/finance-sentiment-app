from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
import torch
from typing import List, Dict, Any
from app.models.schemas import SentimentLabel, SentimentResponse
import asyncio
from asyncio_throttle import Throttler

class SentimentAnalyzer:
    def __init__(self):
        self.model_name = "ProsusAI/finbert"
        self.tokenizer = None
        self.model = None
        self.classifier = None
        self.throttler = Throttler(rate_limit=10, period=1)  # 10 requests per second
        self._load_model()

    def _load_model(self):
        """Load the FinBERT model"""
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForSequenceClassification.from_pretrained(self.model_name)
            self.classifier = pipeline(
                "sentiment-analysis",
                model=self.model,
                tokenizer=self.tokenizer,
                return_all_scores=True
            )
            print("FinBERT model loaded successfully")
        except Exception as e:
            print(f"Error loading model: {e}")
            raise

    async def analyze_sentiment(self, text: str) -> SentimentResponse:
        """Analyze sentiment of financial text"""
        async with self.throttler:
            try:
                if not text or len(text.strip()) < 10:
                    return SentimentResponse(
                        sentiment=SentimentLabel.NEUTRAL,
                        confidence=1.0,
                        raw_scores={"positive": 0.33, "negative": 0.33, "neutral": 0.34}
                    )

                # Preprocess text
                processed_text = self._preprocess_text(text)
                
                # Get sentiment scores
                results = self.classifier(processed_text[:512])[0]  # Limit to 512 tokens
                
                # Convert to our format
                sentiment_scores = {
                    result['label']: result['score'] 
                    for result in results
                }
                
                # Determine dominant sentiment
                dominant_sentiment = max(sentiment_scores, key=sentiment_scores.get)
                confidence = sentiment_scores[dominant_sentiment]
                
                return SentimentResponse(
                    sentiment=SentimentLabel(dominant_sentiment),
                    confidence=confidence,
                    raw_scores=sentiment_scores
                )
                
            except Exception as e:
                print(f"Error in sentiment analysis: {e}")
                return SentimentResponse(
                    sentiment=SentimentLabel.NEUTRAL,
                    confidence=0.5,
                    raw_scores={"positive": 0.33, "negative": 0.33, "neutral": 0.34}
                )

    async def analyze_batch(self, texts: List[str]) -> List[SentimentResponse]:
        """Analyze multiple texts in batch"""
        tasks = [self.analyze_sentiment(text) for text in texts]
        return await asyncio.gather(*tasks)

    def _preprocess_text(self, text: str) -> str:
        """Preprocess text for sentiment analysis"""
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        # Basic cleaning
        text = text.replace('\n', ' ').replace('\r', ' ')
        
        return text.strip()

# Global instance
sentiment_analyzer = SentimentAnalyzer()
