"""Measure the app's sentiment models on labelled financial news headlines.

Test set: the validation split of zeroshot/twitter-financial-news-sentiment (MIT licence),
financial news headlines posted on Twitter and labelled bearish, bullish or neutral. The loaded
split has 2,388 rows; the dataset card's table says 2,486, but the published files hold 2,388.

Methods compared:
- always "neutral" (the most common label);
- the app's keyword list (written before this test was run, not tuned on it);
- TF-IDF + logistic regression trained on the dataset's own train split (9,543 headlines), a
  cheap in-domain baseline that shows what training on this kind of text gives;
- FinBERT, as the app uses it. Its model card says it was fine-tuned on Financial PhraseBank
  (Malo et al., 2014), not on this set.

Each row is one headline, scored on its own. The app also adds article summaries and combines
many headlines; that is not measured here.

  pip install -r backend/requirements.txt -r evaluation/requirements.txt
  python evaluation/evaluate.py            # writes evaluation/results.json
"""

import json
import platform
import sys
import time
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
from app.services.sentiment_analyzer import FINBERT, FINBERT_REVISION, SentimentAnalyzer  # noqa: E402

DATASET = "zeroshot/twitter-financial-news-sentiment"
DATASET_REVISION = "ccbe24de388e287beb92dd393a335c376b350ac3"
LABELS = {0: "negative", 1: "positive", 2: "neutral"}  # bearish, bullish, neutral
CLASSES = ["negative", "neutral", "positive"]


def scores(gold: list[str], pred: list[str]) -> dict:
    per_class = {}
    for c in CLASSES:
        tp = sum(g == p == c for g, p in zip(gold, pred))
        n_pred, n_gold = pred.count(c), gold.count(c)
        precision = tp / n_pred if n_pred else 0.0
        recall = tp / n_gold if n_gold else 0.0
        f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
        per_class[c] = {"precision": round(precision, 4), "recall": round(recall, 4), "f1": round(f1, 4)}
    # confusion[true label][predicted label] = number of headlines
    confusion = {g: {p: sum(1 for a, b in zip(gold, pred) if a == g and b == p) for p in CLASSES} for g in CLASSES}
    return {
        "accuracy": round(sum(g == p for g, p in zip(gold, pred)) / len(gold), 4),
        "macro_f1": round(sum(v["f1"] for v in per_class.values()) / len(CLASSES), 4),
        "per_class": per_class,
        "confusion": confusion,
    }


def tfidf_logreg(train_texts: list[str], train_labels: list[str], test_texts: list[str]) -> list[str]:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.linear_model import LogisticRegression
    from sklearn.pipeline import make_pipeline

    model = make_pipeline(TfidfVectorizer(ngram_range=(1, 2), min_df=2, sublinear_tf=True),
                          LogisticRegression(max_iter=2000, C=10.0))
    model.fit(train_texts, train_labels)
    return list(model.predict(test_texts))


def main() -> None:
    import datasets
    import sklearn
    import torch
    import transformers

    train = datasets.load_dataset(DATASET, split="train", revision=DATASET_REVISION)
    test = datasets.load_dataset(DATASET, split="validation", revision=DATASET_REVISION)
    texts, gold = test["text"], [LABELS[x] for x in test["label"]]
    results = {
        "dataset": f"{DATASET}@{DATASET_REVISION[:8]} (validation)",
        "model": f"{FINBERT}@{FINBERT_REVISION[:8]}",
        "versions": {"python": platform.python_version(), "torch": torch.__version__,
                     "transformers": transformers.__version__, "datasets": datasets.__version__,
                     "scikit-learn": sklearn.__version__},
        "n": len(gold),
        "gold_counts": dict(Counter(gold)),
    }

    majority = Counter(gold).most_common(1)[0][0]
    results["always_" + majority] = scores(gold, [majority] * len(gold))

    methods = {
        "keywords": lambda: [r.sentiment.value for r in SentimentAnalyzer("keywords").predict(texts)],
        "tfidf_logreg": lambda: tfidf_logreg(train["text"], [LABELS[x] for x in train["label"]], texts),
        "finbert": lambda: [r.sentiment.value for r in SentimentAnalyzer("finbert").predict(texts)],
    }
    for name, run in methods.items():
        start = time.perf_counter()
        pred = run()
        results[name] = scores(gold, pred) | {"seconds": round(time.perf_counter() - start, 1)}
        print(f"{name:13s} accuracy {results[name]['accuracy']:.4f}  macro F1 {results[name]['macro_f1']:.4f}")

    out = Path(__file__).with_name("results.json")
    out.write_text(json.dumps(results, indent=2) + "\n")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
