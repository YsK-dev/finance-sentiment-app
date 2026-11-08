"""Turn the collected headlines for a symbol into one result.

Every headline is labelled on its own. The overall label is the most common one, and
`agreement` says what share of the headlines carry it. A fixed rule maps it to BUY (positive),
HOLD (neutral) or SELL (negative); the rule has not been tested against prices.
"""

import re
from collections import Counter
from datetime import datetime, timezone
from typing import Any, Dict, List

from app.models.schemas import AnalysisResult, ScoredArticle, SentimentLabel
from app.services.data_collector import data_collector
from app.services.sentiment_analyzer import sentiment_analyzer

RULE = {SentimentLabel.POSITIVE: "BUY", SentimentLabel.NEUTRAL: "HOLD", SentimentLabel.NEGATIVE: "SELL"}
# On a tie, prefer the more cautious label.
TIE_ORDER = [SentimentLabel.NEUTRAL, SentimentLabel.NEGATIVE, SentimentLabel.POSITIVE]


class NoNewsFound(Exception):
    """No source returned any text for the symbol, so there is nothing to score."""


def _letters(text: str) -> str:
    return re.sub(r"[^a-z0-9]", "", text.lower())


def article_text(article: Dict[str, Any]) -> str:
    """Headline plus summary; the headline alone when the summary only repeats it.

    Google News summaries are "headline outlet" while the title is "headline - outlet", so the
    comparison ignores everything but letters and digits.
    """
    title, summary = article.get("title") or "", article.get("content") or ""
    if not summary or _letters(summary).startswith(_letters(title)[:40]):
        return title
    return f"{title}. {summary}"


def unique_articles(articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Drop articles with no text and repeats of the same headline (feeds overlap)."""
    seen, out = set(), []
    for a in articles:
        key = " ".join((a.get("title") or "").lower().split())
        if key and key not in seen and article_text(a):
            seen.add(key)
            out.append(a)
    return out


class AnalysisEngine:
    async def analyze_symbol(self, symbol: str) -> AnalysisResult:
        articles = unique_articles(await data_collector.get_news_articles(symbol)
                                   + await data_collector.get_feed_posts(symbol))
        if not articles:
            raise NoNewsFound(f"No recent news found for {symbol}.")

        labels = await sentiment_analyzer.analyze_batch([article_text(a) for a in articles])
        counts = Counter(r.sentiment for r in labels)
        overall = max(TIE_ORDER, key=lambda label: counts[label])

        return AnalysisResult(
            symbol=symbol,
            overall_sentiment=overall,
            agreement=counts[overall] / len(labels),
            label_counts={label.value: counts[label] for label in SentimentLabel},
            rule_label=RULE[overall],
            model=labels[0].model,
            articles=[ScoredArticle(title=a["title"], url=a.get("url", ""), source=a.get("source", ""),
                                    published=a.get("published", ""), sentiment=r.sentiment, score=r.confidence)
                      for a, r in zip(articles, labels)],
            timestamp=datetime.now(timezone.utc),
        )


analysis_engine = AnalysisEngine()
