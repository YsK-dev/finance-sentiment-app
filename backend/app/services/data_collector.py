"""Collect recent news about a stock symbol, and YouTube transcripts."""

import asyncio
import os
import re
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import aiohttp
import feedparser
from bs4 import BeautifulSoup
from youtube_transcript_api import YouTubeTranscriptApi

PER_SOURCE = 5  # articles taken from each news source

# General market news feeds. A post is kept only when it names the symbol.
MARKET_FEEDS = {
    "Investing.com": "https://www.investing.com/rss/news.rss",
    "MarketWatch": "https://www.marketwatch.com/rss/topstories",
    "Seeking Alpha": "https://seekingalpha.com/market_currents.xml",
}


def plain_text(html: str) -> str:
    """Feed summaries can be HTML (Google News sends a link and the outlet name); keep only the words."""
    return BeautifulSoup(html or "", "html.parser").get_text(" ", strip=True)


def mentions(symbol: str, text: str) -> bool:
    """True when the text names the ticker as a whole word (AAPL or $AAPL).

    Case-sensitive, so short tickers such as F or ON do not match ordinary words.
    """
    return re.search(rf"(?<![A-Za-z0-9])\$?{re.escape(symbol)}(?![A-Za-z0-9])", text) is not None


def _article(entry: Dict[str, Any], source: str) -> Dict[str, Any]:
    return {
        "title": plain_text(entry.get("title", "")),
        "content": plain_text(entry.get("summary", entry.get("description", ""))),
        "url": entry.get("link", ""),
        "published": entry.get("published", ""),
        "source": source,
    }


async def _feed_entries(url: str) -> list:
    try:
        feed = await asyncio.to_thread(feedparser.parse, url)  # parse() blocks; keep the server responsive
        return feed.entries
    except Exception as e:
        print(f"Feed error {url}: {e}")
        return []


class DataCollector:
    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None
        self.news_api_key = os.getenv("NEWS_API_KEY")
        self.finnhub_api_key = os.getenv("FINNHUB_API_KEY")

    async def get_session(self) -> aiohttp.ClientSession:
        if self.session is None:
            self.session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=20))
        return self.session

    async def close_session(self) -> None:
        if self.session:
            await self.session.close()
            self.session = None

    async def get_news_articles(self, symbol: str) -> List[Dict[str, Any]]:
        """Five articles each from Yahoo Finance and Google News, and from Finnhub and NewsAPI when
        their keys are set. Returns an empty list when nothing answers; never sample data."""
        sources = [self._yahoo(symbol), self._google(symbol)]
        if self.finnhub_api_key:
            sources.append(self._finnhub(symbol))
        if self.news_api_key:
            sources.append(self._newsapi(symbol))
        results = await asyncio.gather(*sources, return_exceptions=True)
        for r in results:
            if isinstance(r, Exception):
                print(f"News source error: {r}")
        return [a for r in results if isinstance(r, list) for a in r]

    async def get_feed_posts(self, symbol: str) -> List[Dict[str, Any]]:
        """Posts from the general market feeds that name the symbol."""
        names = list(MARKET_FEEDS)
        feeds = await asyncio.gather(*(_feed_entries(MARKET_FEEDS[n]) for n in names))
        posts = []
        for name, entries in zip(names, feeds):
            for entry in entries[:10]:
                post = _article(entry, name)
                if mentions(symbol, f"{post['title']} {post['content']}"):
                    posts.append(post)
        return posts

    async def _yahoo(self, symbol: str) -> List[Dict[str, Any]]:
        url = f"https://feeds.finance.yahoo.com/rss/2.0/headline?s={symbol}&region=US&lang=en-US"
        return [_article(e, "Yahoo Finance") for e in (await _feed_entries(url))[:PER_SOURCE]]

    async def _google(self, symbol: str) -> List[Dict[str, Any]]:
        url = f"https://news.google.com/rss/search?q={symbol}+stock+when:7d&hl=en-US&gl=US&ceid=US:en"
        return [_article(e, "Google News") for e in (await _feed_entries(url))[:PER_SOURCE]]

    async def _finnhub(self, symbol: str) -> List[Dict[str, Any]]:
        today = datetime.now()
        url = (f"https://finnhub.io/api/v1/company-news?symbol={symbol}"
               f"&from={(today - timedelta(days=7)):%Y-%m-%d}&to={today:%Y-%m-%d}&token={self.finnhub_api_key}")
        session = await self.get_session()
        async with session.get(url) as response:
            if response.status != 200:
                return []
            data = await response.json()
        return [{"title": item.get("headline", ""), "content": item.get("summary", ""), "url": item.get("url", ""),
                 "published": datetime.fromtimestamp(item.get("datetime", 0)).isoformat(),
                 "source": item.get("source", "Finnhub")} for item in data[:PER_SOURCE]]

    async def _newsapi(self, symbol: str) -> List[Dict[str, Any]]:
        since = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        url = (f"https://newsapi.org/v2/everything?q={symbol}+stock&from={since}"
               f"&sortBy=publishedAt&language=en&apiKey={self.news_api_key}")
        session = await self.get_session()
        async with session.get(url) as response:
            if response.status != 200:
                return []
            data = await response.json()
        return [{"title": item.get("title", ""), "content": item.get("description") or "", "url": item.get("url", ""),
                 "published": item.get("publishedAt", ""), "source": item.get("source", {}).get("name", "NewsAPI")}
                for item in data.get("articles", [])[:PER_SOURCE]]

    async def get_youtube_transcript(self, video_id: str, language: str = "en") -> Optional[str]:
        # The transcript library makes blocking network calls; run it in a thread.
        return await asyncio.to_thread(self._transcript, video_id, language)

    @staticmethod
    def _transcript(video_id: str, language: str) -> Optional[str]:
        """The transcript in `language`, or one that YouTube can translate into it; otherwise None."""
        try:
            listing = YouTubeTranscriptApi().list(video_id)
        except Exception as e:
            print(f"YouTube error for {video_id}: {e}")
            return None
        fetched = None
        try:
            fetched = listing.find_transcript([language]).fetch()
        except Exception:
            for transcript in listing:
                if transcript.is_translatable and any(
                        t.language_code == language for t in transcript.translation_languages):
                    try:
                        fetched = transcript.translate(language).fetch()
                        break
                    except Exception as e:
                        print(f"YouTube translation failed for {video_id}: {e}")
        if fetched is None:
            return None
        return " ".join(snippet.text for snippet in fetched.snippets)


data_collector = DataCollector()
