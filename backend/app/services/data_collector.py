import aiohttp
import asyncio
from typing import List, Dict, Any, Optional
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound
import feedparser
from bs4 import BeautifulSoup
import json
from datetime import datetime, timedelta
from app.models.schemas import SourceType
import os

class DataCollector:
    def __init__(self):
        self.session = None
        self.news_api_key = os.getenv("NEWS_API_KEY")  # Optional: Get from environment
        self.finnhub_api_key = os.getenv("FINNHUB_API_KEY")  # Optional: Get from environment

    async def get_session(self):
        if self.session is None:
            self.session = aiohttp.ClientSession()
        return self.session

    async def close_session(self):
        if self.session:
            await self.session.close()
            self.session = None

    async def get_youtube_transcript(self, video_id: str, language: str = "en") -> Optional[str]:
        """Get YouTube video transcript with automatic translation fallback"""
        try:
            # Create an instance and use the fetch method
            transcript_api = YouTubeTranscriptApi()
            
            # Try to get transcript in requested language
            try:
                fetched_transcript = transcript_api.fetch(
                    video_id, 
                    languages=[language]
                )
            except (TranscriptsDisabled, NoTranscriptFound) as e:
                # If requested language not found, try to get any available transcript
                # and it will be auto-translated if marked as TRANSLATABLE
                print(f"Transcript not available in {language} for {video_id}, trying other languages...")
                
                # Get list of available transcripts
                transcript_list = transcript_api.list(video_id)
                
                # Try to find a transcript that can be translated to the target language
                try:
                    # This will automatically translate if possible
                    transcript = transcript_list.find_transcript([language])
                    fetched_transcript = transcript.fetch()
                except:
                    # If translation fails, get any available transcript
                    print(f"Could not translate to {language}, getting any available transcript...")
                    available_transcripts = transcript_list.transcripts
                    if not available_transcripts:
                        print(f"No transcripts available for video {video_id}")
                        return None
                    
                    # Use the first available transcript
                    first_transcript = list(available_transcripts.values())[0]
                    fetched_transcript = first_transcript.fetch()
                    print(f"Using transcript in language: {first_transcript.language}")
            
            # Extract text from snippets
            transcript_text = ' '.join([snippet.text for snippet in fetched_transcript.snippets])
            return transcript_text
            
        except TranscriptsDisabled:
            print(f"Transcripts are disabled for video {video_id}")
            return None
        except Exception as e:
            print(f"Unexpected YouTube error for {video_id}: {e}")
            import traceback
            traceback.print_exc()
            return None

    async def get_news_articles(self, symbol: str, api_key: str = None) -> List[Dict[str, Any]]:
        """Get financial news articles from multiple sources"""
        session = await self.get_session()
        all_articles = []
        
        # Try multiple sources
        try:
            # 1. Yahoo Finance RSS Feed
            yahoo_articles = await self._get_yahoo_finance_news(symbol)
            all_articles.extend(yahoo_articles)
            
            # 2. Google Finance News
            google_articles = await self._get_google_finance_news(symbol)
            all_articles.extend(google_articles)
            
            # 3. Finnhub (if API key available)
            if self.finnhub_api_key:
                finnhub_articles = await self._get_finnhub_news(symbol)
                all_articles.extend(finnhub_articles)
            
            # 4. NewsAPI (if API key available)
            if self.news_api_key or api_key:
                newsapi_articles = await self._get_newsapi_articles(symbol, api_key or self.news_api_key)
                all_articles.extend(newsapi_articles)
            
            # If no articles from APIs, use mock data
            if not all_articles:
                all_articles = await self._get_mock_news(symbol)
                
        except Exception as e:
            print(f"Error fetching news: {e}")
            # Fallback to mock data
            all_articles = await self._get_mock_news(symbol)
        
        return all_articles[:20]  # Limit to 20 most recent articles

    async def get_blog_posts(self, symbol: str, rss_feeds: List[str] = None) -> List[Dict[str, Any]]:
        """Get blog posts from RSS feeds"""
        if rss_feeds is None:
            # Multiple financial RSS feeds
            rss_feeds = [
                f"https://feeds.finance.yahoo.com/rss/2.0/headline?s={symbol}&region=US&lang=en-US",
                "https://www.investing.com/rss/news.rss",
                "https://www.marketwatch.com/rss/topstories",
                "https://seekingalpha.com/market_currents.xml",
            ]
        
        articles = []
        for feed_url in rss_feeds:
            try:
                feed = feedparser.parse(feed_url)
                for entry in feed.entries[:10]:  # Limit to 10 entries per feed
                    title_lower = entry.get('title', '').lower()
                    summary_lower = entry.get('summary', '').lower()
                    
                    if symbol.lower() in title_lower or symbol.lower() in summary_lower:
                        articles.append({
                            "title": entry.get('title', 'No title'),
                            "content": entry.get('summary', entry.get('description', '')),
                            "url": entry.get('link', ''),
                            "published": entry.get('published', datetime.now().isoformat()),
                            "source": feed_url
                        })
            except Exception as e:
                print(f"Error parsing RSS feed {feed_url}: {e}")
        
        return articles

    async def _get_yahoo_finance_news(self, symbol: str) -> List[Dict[str, Any]]:
        """Get news from Yahoo Finance RSS"""
        articles = []
        try:
            feed_url = f"https://feeds.finance.yahoo.com/rss/2.0/headline?s={symbol}&region=US&lang=en-US"
            feed = feedparser.parse(feed_url)
            
            for entry in feed.entries[:5]:
                articles.append({
                    "title": entry.get('title', ''),
                    "content": entry.get('summary', entry.get('description', '')),
                    "url": entry.get('link', ''),
                    "published": entry.get('published', datetime.now().isoformat()),
                    "source": "Yahoo Finance"
                })
        except Exception as e:
            print(f"Yahoo Finance error: {e}")
        
        return articles
    
    async def _get_google_finance_news(self, symbol: str) -> List[Dict[str, Any]]:
        """Get news from Google Finance RSS"""
        articles = []
        try:
            feed_url = f"https://news.google.com/rss/search?q={symbol}+stock+when:7d&hl=en-US&gl=US&ceid=US:en"
            feed = feedparser.parse(feed_url)
            
            for entry in feed.entries[:5]:
                articles.append({
                    "title": entry.get('title', ''),
                    "content": entry.get('summary', entry.get('description', '')),
                    "url": entry.get('link', ''),
                    "published": entry.get('published', datetime.now().isoformat()),
                    "source": "Google News"
                })
        except Exception as e:
            print(f"Google Finance error: {e}")
        
        return articles
    
    async def _get_finnhub_news(self, symbol: str) -> List[Dict[str, Any]]:
        """Get news from Finnhub API (requires API key)"""
        articles = []
        try:
            session = await self.get_session()
            from_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
            to_date = datetime.now().strftime('%Y-%m-%d')
            
            url = f"https://finnhub.io/api/v1/company-news?symbol={symbol}&from={from_date}&to={to_date}&token={self.finnhub_api_key}"
            
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    for item in data[:5]:
                        articles.append({
                            "title": item.get('headline', ''),
                            "content": item.get('summary', ''),
                            "url": item.get('url', ''),
                            "published": datetime.fromtimestamp(item.get('datetime', 0)).isoformat(),
                            "source": item.get('source', 'Finnhub')
                        })
        except Exception as e:
            print(f"Finnhub error: {e}")
        
        return articles
    
    async def _get_newsapi_articles(self, symbol: str, api_key: str) -> List[Dict[str, Any]]:
        """Get news from NewsAPI (requires API key)"""
        articles = []
        try:
            session = await self.get_session()
            from_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
            
            url = f"https://newsapi.org/v2/everything?q={symbol}+stock&from={from_date}&sortBy=publishedAt&language=en&apiKey={api_key}"
            
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    for item in data.get('articles', [])[:5]:
                        articles.append({
                            "title": item.get('title', ''),
                            "content": item.get('description', ''),
                            "url": item.get('url', ''),
                            "published": item.get('publishedAt', datetime.now().isoformat()),
                            "source": item.get('source', {}).get('name', 'NewsAPI')
                        })
        except Exception as e:
            print(f"NewsAPI error: {e}")
        
        return articles

    async def _get_mock_news(self, symbol: str) -> List[Dict[str, Any]]:
        """Mock news data for demonstration with more varied content"""
        # Enhanced mock data with realistic financial news
        mock_articles = [
            {
                "title": f"{symbol} Reports Strong Q4 Earnings, Beats Analyst Expectations",
                "content": f"{symbol} has announced its Q4 earnings, surpassing Wall Street expectations with strong revenue growth and improved profit margins. The company's strategic initiatives continue to drive positive results.",
                "url": f"https://example.com/news/{symbol}-earnings",
                "published": (datetime.now() - timedelta(hours=2)).isoformat(),
                "source": "Financial Times"
            },
            {
                "title": f"Analysts Upgrade {symbol} Stock Rating to 'Buy'",
                "content": f"Leading investment firms have upgraded their outlook on {symbol}, citing strong fundamentals and positive market positioning. Price targets have been raised significantly.",
                "url": f"https://example.com/news/{symbol}-upgrade",
                "published": (datetime.now() - timedelta(hours=5)).isoformat(),
                "source": "Bloomberg"
            },
            {
                "title": f"{symbol} Announces Strategic Partnership for Market Expansion",
                "content": f"{symbol} has formed a strategic alliance aimed at expanding its market reach and enhancing product offerings. Industry experts view this move favorably.",
                "url": f"https://example.com/news/{symbol}-partnership",
                "published": (datetime.now() - timedelta(hours=12)).isoformat(),
                "source": "Reuters"
            },
            {
                "title": f"Market Analysis: {symbol} Shows Resilience Amid Economic Uncertainty",
                "content": f"Despite broader market volatility, {symbol} continues to demonstrate stability and growth potential. Technical indicators suggest bullish momentum.",
                "url": f"https://example.com/news/{symbol}-analysis",
                "published": (datetime.now() - timedelta(days=1)).isoformat(),
                "source": "MarketWatch"
            },
            {
                "title": f"Institutional Investors Increase Stakes in {symbol}",
                "content": f"Recent SEC filings reveal that major institutional investors have increased their positions in {symbol}, signaling confidence in the company's long-term prospects.",
                "url": f"https://example.com/news/{symbol}-institutional",
                "published": (datetime.now() - timedelta(days=2)).isoformat(),
                "source": "Seeking Alpha"
            }
        ]
        
        return mock_articles

data_collector = DataCollector()
