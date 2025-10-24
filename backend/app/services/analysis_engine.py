from typing import List, Dict, Any
from datetime import datetime, timedelta
from app.models.schemas import SentimentLabel, AnalysisResult, InvestmentAdvice, SourceType
from app.services.sentiment_analyzer import sentiment_analyzer
from app.services.data_collector import data_collector
import numpy as np

class AnalysisEngine:
    def __init__(self):
        self.sentiment_weights = {
            SourceType.NEWS: 0.4,
            SourceType.YOUTUBE: 0.3,
            SourceType.BLOG: 0.2,
            SourceType.SOCIAL: 0.1
        }

    async def analyze_symbol(self, symbol: str, days: int = 7) -> AnalysisResult:
        """Comprehensive analysis for a symbol"""
        
        # Collect data from various sources
        data_sources = await self._collect_data(symbol, days)
        
        # Analyze sentiment for each source
        sentiment_results = await self._analyze_sentiments(data_sources)
        
        # Calculate overall sentiment
        overall_sentiment = self._calculate_overall_sentiment(sentiment_results)
        
        # Generate insights and recommendation
        insights = self._generate_insights(sentiment_results, symbol)
        recommendation = self._generate_recommendation(overall_sentiment, insights)
        
        return AnalysisResult(
            symbol=symbol,
            overall_sentiment=overall_sentiment["sentiment"],
            confidence_score=overall_sentiment["confidence"],
            source_breakdown={
                source: result.confidence 
                for source, result in sentiment_results.items()
            },
            recommendation=recommendation["action"],
            risk_level=recommendation["risk"],
            key_insights=insights,
            timestamp=datetime.now()
        )

    async def get_investment_advice(self, symbol: str) -> InvestmentAdvice:
        """Generate long-term investment advice"""
        analysis = await self.analyze_symbol(symbol)
        
        # Map sentiment to investment action
        action_map = {
            SentimentLabel.POSITIVE: "BUY",
            SentimentLabel.NEUTRAL: "HOLD", 
            SentimentLabel.NEGATIVE: "SELL"
        }
        
        reasoning = [
            f"Overall sentiment: {analysis.overall_sentiment.value}",
            f"Confidence score: {analysis.confidence_score:.2f}",
            f"Risk level: {analysis.risk_level}"
        ]
        
        risk_factors = self._assess_risk_factors(analysis)
        
        return InvestmentAdvice(
            symbol=symbol,
            action=action_map[analysis.overall_sentiment],
            confidence=analysis.confidence_score,
            reasoning=reasoning + analysis.key_insights,
            time_horizon="3-6 months",
            risk_factors=risk_factors
        )

    async def _collect_data(self, symbol: str, days: int) -> Dict[SourceType, List[str]]:
        """Collect data from various sources"""
        data = {}
        
        # Get news articles
        news_articles = await data_collector.get_news_articles(symbol)
        data[SourceType.NEWS] = [article["content"] for article in news_articles]
        
        # Get blog posts
        blog_posts = await data_collector.get_blog_posts(symbol)
        data[SourceType.BLOG] = [post["content"] for post in blog_posts]
        
        return data

    async def _analyze_sentiments(self, data_sources: Dict[SourceType, List[str]]) -> Dict[SourceType, Any]:
        """Analyze sentiment for each data source"""
        results = {}
        
        for source_type, texts in data_sources.items():
            if texts:
                # Analyze all texts for this source
                sentiment_results = await sentiment_analyzer.analyze_batch(texts)
                
                # Average the results
                avg_confidence = np.mean([r.confidence for r in sentiment_results])
                dominant_sentiment = max(
                    set([r.sentiment for r in sentiment_results]),
                    key=[r.sentiment for r in sentiment_results].count
                )
                
                results[source_type] = type('Obj', (object,), {
                    'sentiment': dominant_sentiment,
                    'confidence': avg_confidence
                })()
        
        return results

    def _calculate_overall_sentiment(self, sentiment_results: Dict[SourceType, Any]) -> Dict[str, Any]:
        """Calculate weighted overall sentiment"""
        if not sentiment_results:
            return {"sentiment": SentimentLabel.NEUTRAL, "confidence": 0.5}
        
        total_weight = 0
        sentiment_scores = {label: 0 for label in SentimentLabel}
        
        for source_type, result in sentiment_results.items():
            weight = self.sentiment_weights.get(source_type, 0.1)
            sentiment_scores[result.sentiment] += weight * result.confidence
            total_weight += weight
        
        # Normalize scores
        if total_weight > 0:
            for sentiment in sentiment_scores:
                sentiment_scores[sentiment] /= total_weight
        
        dominant_sentiment = max(sentiment_scores, key=sentiment_scores.get)
        confidence = sentiment_scores[dominant_sentiment]
        
        return {"sentiment": dominant_sentiment, "confidence": confidence}

    def _generate_insights(self, sentiment_results: Dict[SourceType, Any], symbol: str) -> List[str]:
        """Generate key insights from analysis"""
        insights = []
        
        positive_sources = [
            source for source, result in sentiment_results.items() 
            if result.sentiment == SentimentLabel.POSITIVE
        ]
        
        negative_sources = [
            source for source, result in sentiment_results.items() 
            if result.sentiment == SentimentLabel.NEGATIVE
        ]
        
        if positive_sources:
            insights.append(f"Positive sentiment detected from {len(positive_sources)} sources")
        
        if negative_sources:
            insights.append(f"Negative sentiment detected from {len(negative_sources)} sources")
        
        insights.append(f"Analysis based on {len(sentiment_results)} data sources")
        
        return insights

    def _generate_recommendation(self, overall_sentiment: Dict[str, Any], insights: List[str]) -> Dict[str, str]:
        """Generate investment recommendation"""
        sentiment = overall_sentiment["sentiment"]
        confidence = overall_sentiment["confidence"]
        
        if sentiment == SentimentLabel.POSITIVE:
            if confidence > 0.7:
                return {"action": "Consider buying", "risk": "Low"}
            else:
                return {"action": "Monitor for buying opportunity", "risk": "Medium"}
        
        elif sentiment == SentimentLabel.NEGATIVE:
            if confidence > 0.7:
                return {"action": "Consider selling", "risk": "High"}
            else:
                return {"action": "Reduce position", "risk": "Medium"}
        
        else:
            return {"action": "Hold and monitor", "risk": "Low"}

    def _assess_risk_factors(self, analysis: AnalysisResult) -> List[str]:
        """Assess risk factors based on analysis"""
        risk_factors = []
        
        if analysis.confidence_score < 0.6:
            risk_factors.append("Low confidence in sentiment analysis")
        
        if analysis.overall_sentiment == SentimentLabel.NEGATIVE:
            risk_factors.append("Negative market sentiment detected")
        
        if len(analysis.source_breakdown) < 2:
            risk_factors.append("Limited data sources available")
        
        return risk_factors

analysis_engine = AnalysisEngine()
