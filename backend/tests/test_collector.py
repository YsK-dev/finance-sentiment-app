import asyncio
from types import SimpleNamespace

from app.services import data_collector as dc_module
from app.services.analysis_engine import article_text, unique_articles
from app.services.data_collector import MARKET_FEEDS, DataCollector, mentions, plain_text


def test_no_news_gives_an_empty_list_not_made_up_articles(monkeypatch):
    monkeypatch.setattr(dc_module.feedparser, "parse", lambda url: SimpleNamespace(entries=[]))
    collector = DataCollector()
    collector.news_api_key = collector.finnhub_api_key = None
    assert asyncio.run(collector.get_news_articles("ZZZZ")) == []


def test_market_feeds_keep_only_posts_that_name_the_symbol(monkeypatch):
    entries = [{"title": "Apple (AAPL) tops estimates", "summary": ""},
               {"title": "Markets rally on rate hopes", "summary": "Stocks rose across the board."}]
    monkeypatch.setattr(dc_module.feedparser, "parse", lambda url: SimpleNamespace(entries=entries))
    posts = asyncio.run(DataCollector().get_feed_posts("AAPL"))
    assert [p["title"] for p in posts] == ["Apple (AAPL) tops estimates"] * len(MARKET_FEEDS)


def test_the_per_symbol_yahoo_feed_is_not_also_a_market_feed():
    assert not any("yahoo" in url for url in MARKET_FEEDS.values())


def test_ticker_match_is_whole_word_and_case_sensitive():
    assert mentions("AAPL", "Apple (AAPL) rises") and mentions("AAPL", "$AAPL rises")
    assert not mentions("AAPL", "AAPLX fund")
    assert not mentions("ON", "Shares rise on strong demand")
    assert not mentions("F", "Fed holds rates")


def test_html_summaries_become_plain_text():
    html = '<a href="https://news.google.com/x">Apple stock rises</a>&nbsp;&nbsp;<font color="#6f6f6f">Reuters</font>'
    assert plain_text(html) == "Apple stock rises Reuters"


def test_article_text_skips_a_summary_that_repeats_the_headline():
    title = "Apple stock rises after strong iPhone sales - Reuters"
    assert article_text({"title": title, "content": "Apple stock rises after strong iPhone sales Reuters"}) == title
    assert article_text({"title": "Apple rises", "content": "Sales beat estimates."}) == "Apple rises. Sales beat estimates."
    # Google News: the outlet sits inside the first 40 characters of a short headline.
    assert article_text({"title": "AAPL Stock Quote - CNN", "content": "AAPL Stock Quote CNN"}) == "AAPL Stock Quote - CNN"


def test_repeated_headlines_count_once():
    articles = [{"title": "Apple rises"}, {"title": "apple  rises"}, {"title": ""}, {"title": "Apple falls"}]
    assert [a["title"] for a in unique_articles(articles)] == ["Apple rises", "Apple falls"]
