import os
from typing import List, Dict, Any, Optional
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
        self._model_loaded = False
        self._use_lightweight = os.getenv("USE_LIGHTWEIGHT_SENTIMENT", "false").lower() == "true"
        
        # Only load heavy model if not using lightweight mode
        if not self._use_lightweight:
            try:
                self._load_model()
            except Exception as e:
                print(f"Failed to load transformer model, falling back to lightweight: {e}")
                self._use_lightweight = True

    def _load_model(self):
        """Load the FinBERT model (only when not in lightweight mode)"""
        try:
            print("Loading FinBERT model...")
            from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
            
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForSequenceClassification.from_pretrained(self.model_name)
            self.classifier = pipeline(
                "sentiment-analysis",
                model=self.model,
                tokenizer=self.tokenizer,
                return_all_scores=True
            )
            self._model_loaded = True
            print("FinBERT model loaded successfully")
        except Exception as e:
            print(f"Error loading transformer model: {e}")
            raise

    def _lightweight_sentiment_analysis(self, text: str) -> SentimentResponse:
        """
        Lightweight sentiment analysis using simple keyword matching
        This is used when transformer models can't be loaded (e.g., low memory environments)
        """
        text_lower = text.lower()
        
        # Financial sentiment keywords
        positive_keywords = ['profit', 'gain', 'growth', 'increase', 'up', 'rise', 'bullish', 
                           'strong', 'positive', 'beat', 'exceed', 'outperform', 'success']
        negative_keywords = ['loss', 'decline', 'decrease', 'down', 'fall', 'bearish', 
                           'weak', 'negative', 'miss', 'underperform', 'fail', 'risk']
        neutral_keywords = ['stable', 'unchanged', 'maintain', 'hold', 'steady']
        
        # Count keyword occurrences
        positive_count = sum(1 for word in positive_keywords if word in text_lower)
        negative_count = sum(1 for word in negative_keywords if word in text_lower)
        neutral_count = sum(1 for word in neutral_keywords if word in text_lower)
        
        total_count = positive_count + negative_count + neutral_count
        
        if total_count == 0:
            # No sentiment keywords found
            return SentimentResponse(
                sentiment=SentimentLabel.NEUTRAL,
                confidence=0.5,
                raw_scores={"positive": 0.33, "negative": 0.33, "neutral": 0.34}
            )
        
        # Calculate scores
        positive_score = positive_count / total_count
        negative_score = negative_count / total_count
        neutral_score = neutral_count / total_count
        
        # Normalize to sum to 1
        scores = {
            "positive": positive_score,
            "negative": negative_score,
            "neutral": neutral_score
        }
        
        # Determine dominant sentiment
        dominant = max(scores, key=scores.get)
        confidence = scores[dominant]
        
        # Ensure minimum confidence for clear signals
        if confidence < 0.4:
            dominant = "neutral"
            confidence = 0.5
        
        return SentimentResponse(
            sentiment=SentimentLabel(dominant),
            confidence=confidence,
            raw_scores=scores
        )

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

                # Use lightweight analysis if model not loaded
                if self._use_lightweight or not self._model_loaded:
                    return self._lightweight_sentiment_analysis(text)

                # Preprocess text
                processed_text = self._preprocess_text(text)
                
                # Get sentiment scores using transformer model
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
