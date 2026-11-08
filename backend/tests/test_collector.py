import asyncio
from types import SimpleNamespace

from app.services import data_collector as dc_module
from app.services.analysis_engine import article_text
from app.services.data_collector import DataCollector, plain_text


def test_no_news_gives_an_empty_list_not_made_up_articles(monkeypatch):
    monkeypatch.setattr(dc_module.feedparser, "parse", lambda url: SimpleNamespace(entries=[]))
    collector = DataCollector()
    collector.news_api_key = collector.finnhub_api_key = None
    assert asyncio.run(collector.get_news_articles("ZZZZ")) == []


def test_html_summaries_become_plain_text():
    html = '<a href="https://news.google.com/x">Apple stock rises</a>&nbsp;&nbsp;<font color="#6f6f6f">Reuters</font>'
    assert plain_text(html) == "Apple stock rises Reuters"


def test_article_text_skips_a_summary_that_repeats_the_headline():
    title = "Apple stock rises after strong iPhone sales - Reuters"
    assert article_text({"title": title, "content": "Apple stock rises after strong iPhone sales Reuters"}) == title
    assert article_text({"title": "Apple rises", "content": "Sales beat estimates."}) == "Apple rises. Sales beat estimates."
