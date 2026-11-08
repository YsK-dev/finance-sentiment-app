"""Measure the app's sentiment models on labelled financial news headlines.

Test set: the validation split (2,388 headlines) of zeroshot/twitter-financial-news-sentiment
(MIT licence), financial news headlines posted on Twitter, labelled bearish, bullish or neutral.
FinBERT was not trained on it: FinBERT was trained on Financial PhraseBank (2019), and
this set was published in 2022.

  python evaluation/evaluate.py            # writes evaluation/results.json
"""

import json
import sys
import time
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
from app.services.sentiment_analyzer import SentimentAnalyzer  # noqa: E402

DATASET = "zeroshot/twitter-financial-news-sentiment"
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
    return {
        "accuracy": round(sum(g == p for g, p in zip(gold, pred)) / len(gold), 4),
        "macro_f1": round(sum(v["f1"] for v in per_class.values()) / len(CLASSES), 4),
        "per_class": per_class,
    }


def main() -> None:
    from datasets import load_dataset

    data = load_dataset(DATASET, split="validation")
    texts, gold = data["text"], [LABELS[x] for x in data["label"]]
    results = {"dataset": f"{DATASET} (validation)", "n": len(gold), "gold_counts": dict(Counter(gold))}

    majority = Counter(gold).most_common(1)[0][0]
    results["always_" + majority] = scores(gold, [majority] * len(gold))

    for name in ("keywords", "finbert"):
        start = time.perf_counter()
        pred = [r.sentiment.value for r in SentimentAnalyzer(name).predict(texts)]
        results[name] = scores(gold, pred) | {"seconds": round(time.perf_counter() - start, 1)}
        print(name, results[name]["accuracy"], results[name]["macro_f1"])

    out = Path(__file__).with_name("results.json")
    out.write_text(json.dumps(results, indent=2) + "\n")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
