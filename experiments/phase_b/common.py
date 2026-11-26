"""Shared read-only helpers for the Phase B shortcut-learning audit."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any, Iterable

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    brier_score_loss,
    confusion_matrix,
    precision_recall_fscore_support,
    roc_auc_score,
)
from sklearn.naive_bayes import MultinomialNB
from sklearn.svm import LinearSVC

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from prep_cache import light_preprocess, load_cache  # noqa: E402

DATA_DIR = ROOT / "data"
SPLIT_PATH = ROOT / "docs" / "audit_archive" / "duplicate_aware" / "final_v5" / "primary" / "split_manifest.csv"
RANDOM_STATE = 42
MODEL_KEYS = ("lr", "svc", "nb")


def load_grouped_data() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    fake = pd.read_csv(DATA_DIR / "Fake.csv")
    true = pd.read_csv(DATA_DIR / "True.csv")
    frames = []
    for source, frame, label, prefix in (
        ("Fake.csv", fake, 0, "fake"),
        ("True.csv", true, 1, "true"),
    ):
        current = frame[["title", "text", "subject", "date"]].fillna("").copy()
        current["label"] = label
        current["row_id"] = [f"{prefix}:{i}" for i in range(len(current))]
        current["source_file"] = source
        current["source_ordinal"] = np.arange(len(current))
        frames.append(current)
    data = pd.concat(frames, ignore_index=True)
    manifest = pd.read_csv(SPLIT_PATH)
    joined = data.merge(
        manifest[["row_id", "group_id", "partition"]],
        on="row_id",
        how="left",
        validate="one_to_one",
    )
    if joined["partition"].isna().any():
        raise ValueError("Grouped split manifest does not cover every data row")
    if joined.groupby("group_id")["partition"].nunique().gt(1).any():
        raise ValueError("A grouped split crosses train/test partitions")
    train = joined.loc[joined["partition"] == "train"].reset_index(drop=True)
    test = joined.loc[joined["partition"] == "test"].reset_index(drop=True)
    return train, test, joined


def fast_models() -> dict[str, object]:
    return {
        "lr": LogisticRegression(max_iter=1000, C=5.0, random_state=RANDOM_STATE),
        "svc": LinearSVC(C=1.0, max_iter=2000, random_state=RANDOM_STATE),
        "nb": MultinomialNB(alpha=0.01),
    }


def vectorizer() -> TfidfVectorizer:
    return TfidfVectorizer(
        ngram_range=(1, 2),
        max_features=150_000,
        sublinear_tf=True,
        analyzer="word",
        min_df=2,
        max_df=0.95,
    )


def as_probability(model: object, features: Any) -> np.ndarray:
    if hasattr(model, "predict_proba"):
        return np.asarray(model.predict_proba(features))[:, 1]
    scores = np.asarray(model.decision_function(features), dtype=float)
    scores = np.clip(scores, -60.0, 60.0)
    return 1.0 / (1.0 + np.exp(-scores))


def fit_models(train_text: Iterable[str], labels: Iterable[int]) -> tuple[TfidfVectorizer, dict[str, object]]:
    vec = vectorizer()
    train_features = vec.fit_transform(list(train_text))
    models = fast_models()
    for model in models.values():
        model.fit(train_features, pd.Series(labels).reset_index(drop=True))
    return vec, models


def evaluate_models(
    models: dict[str, object],
    vec: TfidfVectorizer,
    texts: Iterable[str],
    labels: Iterable[int],
) -> dict[str, Any]:
    features = vec.transform(list(texts))
    y_true = np.asarray(list(labels), dtype=int)
    output: dict[str, Any] = {}
    for key, model in models.items():
        probabilities = as_probability(model, features)
        predictions = (probabilities >= 0.5).astype(int)
        output[key] = classification_metrics(y_true, predictions, probabilities)
    return output


def classification_metrics(y_true: np.ndarray, predictions: np.ndarray, probabilities: np.ndarray) -> dict[str, Any]:
    precision, recall, f1, support = precision_recall_fscore_support(
        y_true, predictions, labels=[0, 1], zero_division=0
    )
    return {
        "accuracy": float(accuracy_score(y_true, predictions)),
        "per_class": {
            "fake": {"precision": float(precision[0]), "recall": float(recall[0]), "f1": float(f1[0]), "support": int(support[0])},
            "real": {"precision": float(precision[1]), "recall": float(recall[1]), "f1": float(f1[1]), "support": int(support[1])},
        },
        "roc_auc": float(roc_auc_score(y_true, probabilities)),
        "confusion_matrix": confusion_matrix(y_true, predictions, labels=[0, 1]).tolist(),
        "brier_score": float(brier_score_loss(y_true, probabilities)),
    }


def ensemble_predictions(models: dict[str, object], vec: TfidfVectorizer, texts: Iterable[str]) -> tuple[np.ndarray, np.ndarray]:
    features = vec.transform(list(texts))
    probabilities = np.vstack([as_probability(model, features) for model in models.values()]).mean(axis=0)
    return probabilities, (probabilities >= 0.5).astype(int)


def preprocess_rows(frame: pd.DataFrame, title_only: bool = False, body_chars: int | None = None, light: bool = False) -> list[str]:
    cache = None if light or title_only or body_chars is not None else load_cache()
    values = []
    for row in frame.itertuples(index=False):
        title = row.title
        text = "" if title_only else row.text
        if body_chars is not None:
            text = text[:body_chars]
        values.append(cache[row.row_id] if cache is not None else light_preprocess(title, text))
    return values


def first_sentences(text: str, count: int) -> str:
    parts = re.split(r"(?<=[.!?])\s+", text.strip())
    return " ".join(parts[:count])


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
