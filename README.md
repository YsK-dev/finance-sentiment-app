# Finance Sentiment

Type a stock symbol and the app collects recent news headlines about it, labels each one
positive, negative or neutral with [FinBERT](https://huggingface.co/ProsusAI/finbert), and
sums them up. It can also score the transcript of a YouTube video.

FastAPI backend, React frontend, one Docker image.

![Dashboard showing the sentiment of recent Apple headlines](docs/screenshot.png)

## How well the sentiment model works

Measured on the 2,388 labelled headlines in the validation split of
[twitter-financial-news-sentiment](https://huggingface.co/datasets/zeroshot/twitter-financial-news-sentiment)
(financial news headlines posted on Twitter, MIT licence). FinBERT was not trained on this set.

| Method | Accuracy | Macro F1 | Negative headlines found | Positive headlines found |
|---|---|---|---|---|
| Always answer "neutral" | 65.6% | 0.264 | 0% | 0% |
| Keyword list (`SENTIMENT_MODEL=keywords`) | 72.4% | 0.550 | 27.1% | 32.4% |
| **FinBERT (default)** | **72.5%** | **0.668** | **76.1%** | **59.8%** |

"Found" is recall: the share of truly negative (or positive) headlines that the method labels correctly.

What this shows:

- Two out of three headlines are neutral, so accuracy alone flatters weak methods. Macro F1
  weighs the three classes equally and is the fairer number.
- FinBERT's main gain over the keyword list is finding negative and positive news: it finds
  76% of negative headlines, the keyword list 27%.
- FinBERT is far from perfect on this kind of text. When it says "negative" it is right about half
  the time (precision 49%), because it often reads neutral market news as negative.

Reproduce with `python evaluation/evaluate.py` (writes `evaluation/results.json`).

## How a stock gets its label

1. **Collect.** Five recent articles each from Yahoo Finance and Google News (five more each from
   NewsAPI and Finnhub when their API keys are set), plus posts from four financial RSS feeds that
   mention the symbol. If no source returns anything, the API says so (HTTP 404); it never fills in sample data.
2. **Label.** Each headline (with its summary when the summary adds something) goes through FinBERT.
3. **Combine.** The most common label in each source wins, and sources are weighted (news 0.4,
   blogs 0.2). The confidence shown is the model's score for the winning label, weighted the same way.
4. **Map.** A fixed rule turns the result into buy, hold or sell.

## Limits

- **The buy/hold/sell label is not tested against prices.** It is a fixed rule on the
  sentiment, not a trading signal and not financial advice.
- **Most stocks come out neutral,** because most headlines are neutral and each source takes
  its most common label.
- **English only.** FinBERT was trained on English financial text.
- **Long transcripts.** FinBERT reads about 350 words at a time, so a transcript is split into
  300-word pieces (up to 40) and the scores are averaged.
- **YouTube often blocks cloud servers,** so the video page may work only when you run the app
  yourself.

## Run it

**Docker** (one container serves both the API and the web page):

```bash
docker compose up --build
# open http://localhost:8000
```

The image downloads FinBERT (438 MB) while it builds, so the first request does not wait for it.
On a Mac, loading FinBERT and scoring a batch of headlines used up to 1.4 GB of memory.

**Local development:**

```bash
# Backend (Python 3.12)
cd backend
python -m venv .venv && source .venv/bin/activate
pip install --extra-index-url https://download.pytorch.org/whl/cpu -r requirements-dev.txt
uvicorn app.main:app --reload --port 8000

# Frontend, in a second terminal (proxies /api to port 8000)
cd frontend
npm ci && npm run dev
# open http://localhost:3000
```

Settings go in `backend/.env` (see `backend/.env.example`):

| Variable | Meaning |
|---|---|
| `SENTIMENT_MODEL` | `finbert` (default) or `keywords` for machines without enough memory |
| `NEWS_API_KEY`, `FINNHUB_API_KEY` | Optional extra news sources |

## API

Interactive documentation is at `/docs` once the app is running.

| Method and path | What it returns |
|---|---|
| `GET /api/analysis/symbol/{symbol}` | Overall sentiment, score per source, suggested label |
| `GET /api/analysis/advice/{symbol}` | The buy/hold/sell label with its reasoning |
| `GET /api/data/news/{symbol}` | The collected articles |
| `POST /api/sentiment/analyze` | Sentiment of one text: `{"text": "..."}` |
| `POST /api/sentiment/batch` | Sentiment of a JSON list of texts |
| `POST /api/sentiment/youtube/transcript` | Sentiment of a video transcript: `{"video_id": "..."}` |

## Tests

```bash
cd backend
pytest            # fast tests; the news sources are faked, no network needed
pytest -m slow    # also downloads FinBERT and checks it on three clear headlines
```

GitHub Actions runs the fast tests, builds the frontend, and builds and checks the Docker image
on every push.

## Project layout

```
backend/app/
  main.py                      FastAPI app; also serves the built frontend
  routes/                      HTTP endpoints
  services/data_collector.py   news, RSS and YouTube collection
  services/sentiment_analyzer.py  FinBERT and the keyword baseline
  services/analysis_engine.py  combines headline labels into one result
backend/tests/                 pytest tests
evaluation/evaluate.py         the accuracy measurement above
frontend/src/                  React app (Vite, Tailwind)
Dockerfile                     builds the frontend, then the Python image
```

## Licence

The code is released under the MIT License. The FinBERT model is licensed CC BY-NC-SA 4.0, which does not allow
commercial use.
