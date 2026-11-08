import threading
from pathlib import Path

import pytest

from app.services.sentiment_analyzer import FINBERT_REVISION, SentimentAnalyzer, keyword_sentiment


def test_keywords_positive_and_negative():
    assert keyword_sentiment("Apple beats estimates as profits rise").sentiment.value == "positive"
    assert keyword_sentiment("Shares fall after the company misses guidance").sentiment.value == "negative"


def test_keywords_match_whole_words_only():
    # "update", "support", "supply" and "group" contain "up"; they must not count as positive.
    result = keyword_sentiment("Company posts an update on supply, support and group structure")
    assert result.sentiment.value == "neutral"
    assert result.model == "keywords"


def test_keywords_no_signal_is_neutral():
    result = keyword_sentiment("The annual meeting takes place on Tuesday")
    assert result.sentiment.value == "neutral"
    assert result.confidence == 0.5


def test_unknown_model_name_is_rejected():
    with pytest.raises(ValueError):
        SentimentAnalyzer("gpt")


@pytest.mark.slow
def test_finbert_labels_clear_headlines():
    texts = ["Company reports record profit and raises its full-year outlook",
             "Company swings to a large loss and cuts its dividend",
             "Company will hold its annual meeting on Tuesday"]
    labels = [r.sentiment.value for r in SentimentAnalyzer("finbert").predict(texts)]
    assert labels == ["positive", "negative", "neutral"]


def test_long_text_is_scored_in_pieces_and_averaged():
    import asyncio
    text = "profits rise " * 400 + "the meeting is on Tuesday " * 80  # 800 + 400 words
    result = asyncio.run(SentimentAnalyzer("keywords").analyze_long_text(text, words_per_chunk=400))
    assert result.chunks == 3
    # Two positive pieces and one neutral piece: positive 2/3 on average.
    assert result.sentiment.value == "positive"
    assert abs(result.confidence - 2 / 3) < 1e-9


def test_concurrent_first_requests_load_the_model_once(monkeypatch):
    loads = []

    def fake_load(self):
        loads.append(1)
        threading.Event().wait(0.2)  # a slow load, so the threads overlap
        return lambda texts, **kw: [[{"label": "neutral", "score": 1.0}] for _ in texts]

    monkeypatch.setattr(SentimentAnalyzer, "_load", fake_load)
    analyzer = SentimentAnalyzer("finbert")
    threads = [threading.Thread(target=analyzer.predict, args=(["text"],)) for _ in range(4)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert len(loads) == 1


def test_docker_image_downloads_the_same_model_revision():
    dockerfile = (Path(__file__).resolve().parents[2] / "Dockerfile").read_text()
    assert f"FINBERT_REVISION={FINBERT_REVISION}" in dockerfile
