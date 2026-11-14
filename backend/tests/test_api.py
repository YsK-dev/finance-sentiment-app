import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.main import add_frontend, app
from app.services.analysis_engine import data_collector
from app.services.sentiment_analyzer import sentiment_analyzer

client = TestClient(app)


@pytest.fixture(autouse=True)
def keyword_model(monkeypatch):
    # The word list keeps these tests fast and offline; FinBERT is covered by the slow test.
    monkeypatch.setattr(sentiment_analyzer, "model", "keywords")


def fake_sources(monkeypatch, news, posts=()):
    async def get_news_articles(symbol):
        return list(news)

    async def get_feed_posts(symbol):
        return list(posts)

    monkeypatch.setattr(data_collector, "get_news_articles", get_news_articles)
    monkeypatch.setattr(data_collector, "get_feed_posts", get_feed_posts)


def article(title, source="Test"):
    return {"title": title, "content": "", "url": "https://example.org", "source": source, "published": ""}


def test_health():
    assert client.get("/health").json()["status"] == "healthy"


def test_symbol_analysis_counts_each_headline(monkeypatch):
    fake_sources(monkeypatch,
                 news=[article("TEST beats estimates as profits rise"), article("TEST shares surge to a record"),
                       article("TEST holds its annual meeting")],
                 posts=[article("TEST shares surge to a record", "Feed")])  # same headline in two places
    body = client.get("/api/analysis/symbol/test").json()
    assert body["symbol"] == "TEST"
    assert body["label_counts"] == {"positive": 2, "negative": 0, "neutral": 1}  # the repeat counts once
    assert body["overall_sentiment"] == "positive"
    assert body["agreement"] == pytest.approx(2 / 3)
    assert body["rule_label"] == "BUY"
    assert [a["sentiment"] for a in body["articles"]] == ["positive", "positive", "neutral"]


def test_a_tie_gives_the_cautious_label(monkeypatch):
    fake_sources(monkeypatch, news=[article("Profits rise"), article("Profits fall")])
    body = client.get("/api/analysis/symbol/test").json()
    assert body["overall_sentiment"] == "neutral" and body["rule_label"] == "HOLD"


def test_symbol_without_news_returns_404(monkeypatch):
    fake_sources(monkeypatch, news=[])
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


def test_frontend_files_and_page_routes(tmp_path):
    dist = tmp_path / "dist"
    (dist / "assets").mkdir(parents=True)
    (dist / "index.html").write_text("<div id=\"root\"></div>")
    (dist / "assets" / "app.js").write_text("console.log(1)")
    (tmp_path / "secret.txt").write_text("outside the folder")
    web = FastAPI()
    add_frontend(web, dist)
    c = TestClient(web)
    assert c.get("/").text == "<div id=\"root\"></div>"
    assert c.get("/youtube").text == "<div id=\"root\"></div>"  # client-side route
    assert c.get("/assets/app.js").text == "console.log(1)"
    assert c.head("/").status_code == 200
    assert c.get("/api/unknown").status_code == 404
    assert c.get("/%2e%2e/secret.txt").text == "<div id=\"root\"></div>"  # never serves files outside dist
