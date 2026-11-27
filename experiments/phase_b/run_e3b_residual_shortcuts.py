"""E3b: residual source, format, time, and topic shortcut audit."""

from __future__ import annotations

import re
from collections import Counter
from pathlib import Path

import numpy as np
from common import (
    classification_metrics,
    evaluate_models,
    fit_models,
    light_preprocess,
    load_grouped_data,
    preprocess_rows,
    vectorizer,
    write_json,
)
from prep_cache import nlp
from run_e3_marker_stripping import strip_source_markers
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

SEED = 42
WEEKDAYS = r"monday|tuesday|wednesday|thursday|friday|saturday|sunday"
MONTHS = r"january|february|march|april|may|june|july|august|september|october|november|december|jan|feb|mar|apr|jun|jul|aug|sep|oct|nov|dec"
OUTLETS = r"reuters|associated press|ap news|cnn|fox news|fox|breitbart|daily wire|21st century wire|getty|new york times|washington post|bbc|abc news|nbc|cbs"
FORMAT_TERMS = r"featured image|image via|image credit|photo by|read more|pic twitter|twitter com|https? com|video|image|photo|screenshot|watch|subscribe|click here"
TIME_TOPIC_TERMS = r"washington|london|new york|moscow|beijing|china|britain|parliament|republican|democratic|trump|obama|clinton|hillary|isis|election|president|senator|congress|government"


def strip_source_markers_v2(text: str, title: str = "") -> tuple[str, str]:
    """E3b stripper: v1 plus residual outlet, date, social, image, and CTA tokens."""
    title, text = strip_source_markers(text, title)

    def clean(value: str) -> str:
        value = re.sub(r"(?:" + OUTLETS + r")", " ", value, flags=re.I)
        value = re.sub(r"(?:" + FORMAT_TERMS + r")", " ", value, flags=re.I)
        value = re.sub(r"\b(?:" + WEEKDAYS + r"|" + MONTHS + r")\b", " ", value, flags=re.I)
        value = re.sub(
            r"\b(?:https?://\S+|www\.\S+|pic\.twitter\.com/\S+|twitter\.com/\S+)\b",
            " ",
            value,
            flags=re.I,
        )
        value = re.sub(r"\b(?:com|org|net)\b", " ", value, flags=re.I)
        return re.sub(r"\s+", " ", value).strip()

    return clean(title), clean(text)


def stripped_values(frame, version: str) -> list[str]:
    stripper = strip_source_markers if version == "v1" else strip_source_markers_v2
    return [
        light_preprocess(*stripper(row.text, row.title)) for row in frame.itertuples(index=False)
    ]


def raw_stripped(frame, version: str) -> list[tuple[str, str]]:
    stripper = strip_source_markers if version == "v1" else strip_source_markers_v2
    return [stripper(row.text, row.title) for row in frame.itertuples(index=False)]


def fit_condition(train_text, test_text, train, test):
    vec, models = fit_models(train_text, train["label"])
    return evaluate_models(models, vec, test_text, test["label"])


def char_probe(train_raw, test_raw, labels_train, labels_test):
    train_text = [body[:50] for _, body in train_raw]
    test_text = [body[:50] for _, body in test_raw]
    vec = TfidfVectorizer(analyzer="char", ngram_range=(3, 5), min_df=2, max_features=50_000)
    train_matrix = vec.fit_transform(train_text)
    test_matrix = vec.transform(test_text)
    model = LogisticRegression(max_iter=1000, random_state=SEED).fit(train_matrix, labels_train)
    probabilities = model.predict_proba(test_matrix)[:, 1]
    return classification_metrics(
        np.asarray(labels_test), (probabilities >= 0.5).astype(int), probabilities
    )


def classify_feature(feature: str) -> str:
    normalized = feature.lower()
    if re.search(OUTLETS + "|" + FORMAT_TERMS, normalized):
        return "outlet/format artifact"
    if re.search(WEEKDAYS + "|" + MONTHS + "|" + TIME_TOPIC_TERMS, normalized):
        return "time/topic artifact"
    return "content word"


def top_features(texts, labels):
    vec = vectorizer()
    matrix = vec.fit_transform(texts)
    model = LogisticRegression(max_iter=1000, C=5.0, random_state=SEED).fit(matrix, labels)
    names, weights = vec.get_feature_names_out(), model.coef_[0]
    output = {}
    for label, indices in (
        ("fake", weights.argsort()[:50]),
        ("real", weights.argsort()[-50:][::-1]),
    ):
        rows = [
            {
                "feature": str(names[i]),
                "weight": float(weights[i]),
                "category": classify_feature(str(names[i])),
            }
            for i in indices
        ]
        counts = Counter(row["category"] for row in rows)
        output[label] = {
            "features": rows,
            "percentages": {
                key: counts[key] * 2.0
                for key in ("content word", "outlet/format artifact", "time/topic artifact")
            },
            "remaining_artifacts": [
                row["feature"] for row in rows if row["category"] != "content word"
            ],
        }
    return output


def topic_counts(frame, version: str):
    counts = {0: Counter(), 1: Counter()}
    for row, label in zip(raw_stripped(frame, version), frame["label"]):
        tokens = re.findall(r"\b[A-Z][a-z]{2,}\b", row[0] + " " + row[1])
        counts[int(label)].update(
            token.lower() for token in tokens if token.lower() not in nlp.Defaults.stop_words
        )
    top = {"fake": counts[0].most_common(30), "real": counts[1].most_common(30)}
    return {"top_30": top, "overlap": sorted(set(dict(top["fake"])) & set(dict(top["real"])))}


def examples(frame):
    output = {}
    for label, name in ((0, "fake"), (1, "real")):
        candidates = frame.loc[frame["label"] == label].sample(n=30, random_state=SEED)
        output[name] = []
        for row in candidates.itertuples(index=False):
            title, body = strip_source_markers(row.text, row.title)
            output[name].append({"title": title[:200], "text": body[:200]})
            line = f"[{name}] {title[:200]} | {body[:200]}"
            print(line.encode("ascii", "replace").decode("ascii"))
    return output


def main() -> None:
    train, test, _ = load_grouped_data()
    original_train, original_test = (
        preprocess_rows(train, light=True),
        preprocess_rows(test, light=True),
    )
    v1_train, v1_test = stripped_values(train, "v1"), stripped_values(test, "v1")
    v2_train, v2_test = stripped_values(train, "v2"), stripped_values(test, "v2")
    conditions = {
        "v1_train_v1_test": fit_condition(v1_train, v1_test, train, test),
        "original_train_v1_test": fit_condition(original_train, v1_test, train, test),
        "v1_train_original_test": fit_condition(v1_train, original_test, train, test),
        "v2_train_v2_test": fit_condition(v2_train, v2_test, train, test),
        "original_train_v2_test": fit_condition(original_train, v2_test, train, test),
        "v2_train_original_test": fit_condition(v2_train, original_test, train, test),
    }
    output = {
        "experiment": "E3b",
        "seed": SEED,
        "examples_v1_test": examples(test),
        "char_first_50": {
            "v1": char_probe(
                raw_stripped(train, "v1"), raw_stripped(test, "v1"), train["label"], test["label"]
            ),
            "v2": char_probe(
                raw_stripped(train, "v2"), raw_stripped(test, "v2"), train["label"], test["label"]
            ),
        },
        "top_features_v1": top_features(v1_train, train["label"]),
        "conditions": conditions,
        "topic_time_counts_v1": topic_counts(test, "v1"),
    }
    write_json(Path(__file__).with_name("e3b_residual_shortcuts.json"), output)


if __name__ == "__main__":
    main()
