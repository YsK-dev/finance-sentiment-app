import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services.analysis_engine import data_collector
from app.services.sentiment_analyzer import sentiment_analyzer

client = TestClient(app)


@pytest.fixture(autouse=True)
def keyword_model(monkeypatch):
    # The word list keeps these tests fast and offline; FinBERT is covered by the slow test.
    monkeypatch.setattr(sentiment_analyzer, "model", "keywords")


def fake_news(articles):
    async def get_news_articles(symbol, api_key=None):
        return articles

    async def get_blog_posts(symbol, rss_feeds=None):
        return []

    return get_news_articles, get_blog_posts


def test_health():
    assert client.get("/health").json()["status"] == "healthy"


def test_symbol_analysis_uses_the_collected_news(monkeypatch):
    news, blogs = fake_news([{"title": "TEST beats estimates as profits rise", "content": ""},
                             {"title": "TEST shares surge to a record", "content": ""}])
    monkeypatch.setattr(data_collector, "get_news_articles", news)
    monkeypatch.setattr(data_collector, "get_blog_posts", blogs)
    body = client.get("/api/analysis/symbol/test").json()
    assert body["symbol"] == "TEST"
    assert body["overall_sentiment"] == "positive"


def test_symbol_without_news_returns_404(monkeypatch):
    news, blogs = fake_news([])
    monkeypatch.setattr(data_collector, "get_news_articles", news)
    monkeypatch.setattr(data_collector, "get_blog_posts", blogs)
    response = client.get("/api/analysis/symbol/zzzz")
    assert response.status_code == 404
    assert "No recent news" in response.json()["detail"]


def test_text_endpoint_reports_the_model():
    body = client.post("/api/sentiment/analyze", json={"text": "Profits fall and the outlook is weak"}).json()
    assert body["sentiment"] == "negative"
    assert body["model"] == "keywords"


def test_batch_endpoint_takes_a_json_list():
    body = client.post("/api/sentiment/batch", json=["Profits rise strongly", "Nothing to report"]).json()
    assert [r["sentiment"] for r in body["results"]] == ["positive", "neutral"]
