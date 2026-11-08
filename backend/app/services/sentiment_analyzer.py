"""Financial sentiment: FinBERT by default, or a keyword baseline.

SENTIMENT_MODEL=finbert (default) loads ProsusAI/finbert (a 438 MB download).
SENTIMENT_MODEL=keywords uses a small word list instead. It is much weaker (see the README's
evaluation table) and exists only as a baseline and for machines that cannot hold the model.
"""

import asyncio
import os
import re
from typing import List

from app.models.schemas import SentimentLabel, SentimentResponse

FINBERT = "ProsusAI/finbert"

POSITIVE_WORDS = {"profit", "profits", "gain", "gains", "growth", "increase", "increases", "rise", "rises",
                  "bullish", "strong", "positive", "beat", "beats", "exceed", "exceeds", "outperform",
                  "upgrade", "upgrades", "success", "record", "surge", "surges", "jump", "jumps"}
NEGATIVE_WORDS = {"loss", "losses", "decline", "declines", "decrease", "decreases", "fall", "falls", "drop",
                  "drops", "bearish", "weak", "negative", "miss", "misses", "underperform", "downgrade",
                  "downgrades", "fail", "fails", "cut", "cuts", "lawsuit", "plunge", "plunges"}
WORD = re.compile(r"[a-z']+")


def keyword_sentiment(text: str) -> SentimentResponse:
    """Count whole words from two short lists; no match means neutral."""
    words = WORD.findall(text.lower())
    pos = sum(w in POSITIVE_WORDS for w in words)
    neg = sum(w in NEGATIVE_WORDS for w in words)
    total = pos + neg
    if total == 0 or pos == neg:
        return SentimentResponse(sentiment=SentimentLabel.NEUTRAL, confidence=0.5,
                                 raw_scores={"positive": 0.0, "negative": 0.0, "neutral": 1.0}, model="keywords")
    label = SentimentLabel.POSITIVE if pos > neg else SentimentLabel.NEGATIVE
    return SentimentResponse(sentiment=label, confidence=max(pos, neg) / total,
                             raw_scores={"positive": pos / total, "negative": neg / total, "neutral": 0.0},
                             model="keywords")


class SentimentAnalyzer:
    def __init__(self, model: str | None = None):
        self.model = (model or os.getenv("SENTIMENT_MODEL", "finbert")).lower()
        if self.model not in ("finbert", "keywords"):
            raise ValueError(f"SENTIMENT_MODEL must be 'finbert' or 'keywords', not {self.model!r}")
        self._classifier = None

    def _finbert(self):
        # Loaded on first use so that importing the app (and the tests) stays fast.
        if self._classifier is None:
            from transformers import pipeline
            self._classifier = pipeline("text-classification", model=FINBERT, top_k=None)
        return self._classifier

    def predict(self, texts: List[str]) -> List[SentimentResponse]:
        """Label a list of texts in one batch. Blocking; the async methods run it in a thread."""
        texts = [" ".join(t.split()) for t in texts]
        if self.model == "keywords":
            return [keyword_sentiment(t) for t in texts]
        out = self._finbert()(texts, batch_size=16, truncation=True, max_length=512)
        results = []
        for scores in out:
            raw = {s["label"]: float(s["score"]) for s in scores}
            label = max(raw, key=raw.get)
            results.append(SentimentResponse(sentiment=SentimentLabel(label), confidence=raw[label],
                                             raw_scores=raw, model="finbert"))
        return results

    async def analyze_long_text(self, text: str, words_per_chunk: int = 300,
                                max_chunks: int = 40) -> SentimentResponse:
        """Score a long text (a video transcript) in pieces and average the scores.

        FinBERT reads at most 512 tokens, about 350 English words, so one call would only
        see the start. Up to `max_chunks` pieces (12,000 words by default) are scored.
        """
        words = text.split()
        chunks = [" ".join(words[i:i + words_per_chunk])
                  for i in range(0, len(words), words_per_chunk)][:max_chunks] or [""]
        results = await self.analyze_batch(chunks)
        labels = sorted({k for r in results for k in r.raw_scores})
        mean = {k: sum(r.raw_scores.get(k, 0.0) for r in results) / len(results) for k in labels}
        label = max(mean, key=mean.get)
        return SentimentResponse(sentiment=SentimentLabel(label), confidence=mean[label], raw_scores=mean,
                                 model=results[0].model, chunks=len(results))

    async def analyze_sentiment(self, text: str) -> SentimentResponse:
        return (await self.analyze_batch([text]))[0]

    async def analyze_batch(self, texts: List[str]) -> List[SentimentResponse]:
        if not texts:
            return []
        return await asyncio.to_thread(self.predict, texts)


sentiment_analyzer = SentimentAnalyzer()
