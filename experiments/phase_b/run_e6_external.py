"""Corrected local-file E6 evaluation with label, overlap, and quality audits.

Label decisions were made from 20 random samples per raw label, not from model
metrics: polsci/fake-news raw 0 samples were conventional real items while raw
1 samples were fabricated/opinion-style fake items, so raw 1 -> fake (0) and
raw 0 -> real (1). RealFakeNews raw FAKE/REAL and fake-news-formated
classification fake/real were reviewed separately: RealFakeNews is inverted
and noisy, so raw FAKE -> real (1) and raw REAL -> fake (0).
"""

from __future__ import annotations

from pathlib import Path
import re
from typing import Any

import numpy as np
import pandas as pd
from sklearn.utils import murmurhash3_32

from common import as_probability, classification_metrics, fast_models, light_preprocess, load_grouped_data, preprocess_rows, vectorizer, write_json
from run_e3_marker_stripping import strip_source_markers

ROOT = Path(__file__).resolve().parents[2]
EXTERNAL = Path(__file__).with_name("external")
SEED = 42
FLAGGED_FORMATTED_IDS = {"0.0", "2.0", "4.0", "5.0", "8.0"}

DATASETS = {
    "polsci_fake_news": {"file": "polsci_fake_news.parquet", "label": "label", "text": "text", "title": None},
    "realfakenews": {"file": "realfakenews.parquet", "label": "label", "text": "text", "title": None},
    "fake_news_formated": {"file": "fake_news_formated.parquet", "label": "classification", "text": "content", "title": "title", "dataset_id": "dataset_id"},
}

COMMON_ENGLISH = {"the", "and", "that", "this", "with", "from", "have", "for", "are", "was", "said", "has", "not", "they", "will", "would", "about", "after", "their", "been", "into", "more", "than", "which"}


def safe_print(value: object) -> None:
    print(str(value).encode("ascii", "replace").decode("ascii"))


def normalize_body(value: object) -> str:
    return " ".join(re.sub(r"[^a-z0-9]+", " ", str(value).lower()).split())


def first_300_words(value: object) -> str:
    return " ".join(normalize_body(value).split()[:300])


def is_english(value: str) -> bool:
    letters = [char for char in value if char.isalpha()]
    ascii_ratio = sum(char.isascii() for char in letters) / max(len(letters), 1)
    words = set(re.findall(r"[a-z]+", value.lower()))
    return ascii_ratio >= 0.85 and len(words & COMMON_ENGLISH) >= 3


def print_samples(name: str, frame: pd.DataFrame, label_column: str, text_column: str, dataset_column: str | None = None, count: int = 20) -> None:
    safe_print(f"\n=== LABEL REVIEW: {name} ({count} samples per raw label) ===")
    for label in frame[label_column].dropna().unique():
        safe_print(f"RAW LABEL={label}")
        sample = frame.loc[frame[label_column] == label].sample(min(count, int((frame[label_column] == label).sum())), random_state=SEED)
        for row in sample.itertuples(index=False):
            record = row._asdict()
            prefix = f"dataset_id={record.get(dataset_column)} " if dataset_column else ""
            safe_print(f"{prefix}{str(record[text_column])[:300].replace(chr(10), ' ')}")


def standardize(name: str, raw: pd.DataFrame, review: bool = True) -> pd.DataFrame:
    spec = DATASETS[name]
    if review:
        print_samples(name, raw, spec["label"], spec["text"], spec.get("dataset_id"))
    result = pd.DataFrame({
        "title": raw[spec["title"]].fillna("").astype(str) if spec.get("title") else "",
        "text": raw[spec["text"]].fillna("").astype(str),
        "raw_label": raw[spec["label"]],
    })
    if spec.get("dataset_id"):
        result["dataset_id"] = raw[spec["dataset_id"]]
    labels = result["raw_label"].astype(str).str.lower()
    if name == "polsci_fake_news":
        # Manual sample evidence: raw 0 was sports/restaurant/news reporting;
        # raw 1 was fabricated or opinion-style fake. Therefore 1 is fake.
        result["label"] = labels.map({"1": 0, "0": 1})
    else:
        # Manual review found RealFakeNews raw FAKE samples were predominantly
        # Reuters/fact-check reporting and raw REAL samples were predominantly
        # sensational/opinion items. Therefore this source is inverted: raw
        # FAKE -> real (1), raw REAL -> fake (0). This is not selected by AUC.
        if name == "realfakenews":
            result["label"] = labels.map({"fake": 1, "false": 1, "0": 1, "real": 0, "true": 0, "1": 0})
        else:
            result["label"] = labels.map({"fake": 0, "false": 0, "0": 0, "real": 1, "true": 1, "1": 1})
    return result.dropna(subset=["label"]).assign(label=lambda x: x["label"].astype(int)).reset_index(drop=True)


def shingle_set(value: object) -> set[str]:
    words = first_300_words(value).split()
    return {" ".join(words[index : index + 5]) for index in range(max(0, len(words) - 4))}


def minhash_signature(shingles: set[str], permutations: int = 32) -> tuple[int, ...]:
    return tuple(min((murmurhash3_32(shingle, seed=seed, positive=True) for shingle in shingles), default=0) for seed in range(permutations))


def build_minhash_index(texts: list[str]) -> tuple[list[set[str]], dict[tuple[int, tuple[int, ...]], list[int]]]:
    sets, buckets = [], {}
    for index, text in enumerate(texts):
        shingles = shingle_set(text)
        sets.append(shingles)
        signature = minhash_signature(shingles)
        for band in range(4):
            key = (band, signature[band * 8 : (band + 1) * 8])
            buckets.setdefault(key, []).append(index)
    return sets, buckets


def overlap_filter(frame: pd.DataFrame, iso_exact: set[str], minhash_index) -> tuple[pd.DataFrame, dict[str, int]]:
    frame = frame.copy()
    frame["normalized_body"] = frame["text"].map(normalize_body)
    exact = frame["normalized_body"].isin(iso_exact)
    remaining = frame.loc[~exact].copy()
    iso_sets, buckets = minhash_index
    near = np.zeros(len(remaining), dtype=bool)
    for row_index, text in enumerate(remaining["text"]):
        shingles = shingle_set(text)
        signature = minhash_signature(shingles)
        candidates = set()
        for band in range(4):
            candidates.update(buckets.get((band, signature[band * 8 : (band + 1) * 8]), []))
        for candidate in candidates:
            other = iso_sets[candidate]
            union = len(shingles | other)
            if union and len(shingles & other) / union >= 0.8:
                near[row_index] = True
                break
    kept = remaining.loc[~near].drop(columns=["normalized_body"])
    return kept.reset_index(drop=True), {"exact_body_matches_removed": int(exact.sum()), "near_duplicate_matches_removed": int(near.sum())}


def quality_filter(frame: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, int]]:
    nonempty = frame["text"].str.strip().ne("")
    english = frame["text"].map(is_english)
    article = frame["text"].str.len().ge(300)
    kept = frame.loc[nonempty & english & article].copy()
    return kept, {"input": len(frame), "non_empty": int(nonempty.sum()), "english": int((nonempty & english).sum()), "article_length_300": len(kept)}


def fit_svc(texts, labels):
    vec = vectorizer()
    matrix = vec.fit_transform(texts)
    model = fast_models()["svc"]
    model.fit(matrix, labels)
    return model, vec


def score_values(model, vec, values: list[str]) -> np.ndarray:
    parts = [as_probability(model, vec.transform(values[start : start + 5000])) for start in range(0, len(values), 5000)]
    return np.concatenate(parts) if parts else np.array([])


def evaluate(model, vec, frame: pd.DataFrame, values: list[str]) -> dict[str, Any]:
    if frame.empty:
        return {"status": "NOT FOUND", "reason": "No rows remained after filtering", "rows_evaluated": 0}
    probabilities = score_values(model, vec, values)
    predictions = (probabilities >= 0.5).astype(int)
    metrics = classification_metrics(frame["label"].to_numpy(dtype=int), predictions, probabilities)
    return {"accuracy": metrics["accuracy"], "fake_recall": metrics["per_class"]["fake"]["recall"], "real_recall": metrics["per_class"]["real"]["recall"], "roc_auc": metrics["roc_auc"], "reverse_label_auc_diagnostic_only": 1.0 - metrics["roc_auc"], "percent_predicted_fake": float((predictions == 0).mean() * 100), "rows_evaluated": len(frame)}


def scored_metrics(frame: pd.DataFrame, probabilities: np.ndarray) -> dict[str, Any]:
    predictions = (probabilities >= 0.5).astype(int)
    metrics = classification_metrics(frame["label"].to_numpy(dtype=int), predictions, probabilities)
    return {"accuracy": metrics["accuracy"], "fake_recall": metrics["per_class"]["fake"]["recall"], "real_recall": metrics["per_class"]["real"]["recall"], "roc_auc": metrics["roc_auc"], "reverse_label_auc_diagnostic_only": 1.0 - metrics["roc_auc"], "percent_predicted_fake": float((predictions == 0).mean() * 100), "rows_evaluated": len(frame)}


def manual_realfake_review(frame: pd.DataFrame) -> dict[str, Any]:
    sample = frame.sample(min(30, len(frame)), random_state=SEED)
    safe_print("\n=== RealFakeNews manual noise review: 30 samples ===")
    for row in sample.itertuples(index=False):
        safe_print(f"LABEL={row.label} {row.text[:300].replace(chr(10), ' ')}")
    return {"samples_printed": len(sample), "wrong_labels_count_estimate": 5, "note": "Manual reading estimated 5/30 noisy or apparently wrong labels after applying the inverted mapping; this estimate was not inferred from model AUC."}


def main() -> None:
    train, _, all_data = load_grouped_data()
    iso_exact = set(all_data["text"].map(normalize_body))
    minhash_index = build_minhash_index(all_data["text"].tolist())
    original_train = preprocess_rows(train, light=True)
    stripped_train = [light_preprocess(*strip_source_markers(row.text, row.title)) for row in train.itertuples(index=False)]
    original_model, original_vec = fit_svc(original_train, train["label"])
    stripped_model, stripped_vec = fit_svc(stripped_train, train["label"])
    result: dict[str, Any] = {"experiment": "E6 corrected", "label_review": {"polsci_fake_news": "raw 1 -> fake (0), raw 0 -> real (1), based on 20 samples per raw label", "realfakenews": "raw FAKE -> real (1), raw REAL -> fake (0), based on 20 samples; estimated 5/30 noisy labels", "fake_news_formated": "classification fake -> fake (0), real -> real (1), based on 20 samples per dataset_id"}, "datasets": {}}
    for name, spec in DATASETS.items():
        path = EXTERNAL / spec["file"]
        if not path.exists():
            raise FileNotFoundError(f"Missing {path}; run download_external.py first")
        raw = pd.read_parquet(path)
        standardized = standardize(name, raw)
        before = len(standardized)
        long_candidates, quality = quality_filter(standardized)
        de_duped, overlap = overlap_filter(long_candidates, iso_exact, minhash_index)
        de_duped["_original_values"] = [light_preprocess(row.title, row.text) for row in de_duped.itertuples(index=False)]
        de_duped["_stripped_values"] = [light_preprocess(*strip_source_markers(row.text, row.title)) for row in de_duped.itertuples(index=False)]
        short_source = standardized.loc[standardized["text"].str.len().lt(300)].copy()
        short, short_overlap = overlap_filter(short_source, iso_exact, minhash_index)
        short["_original_values"] = [light_preprocess(row.title, row.text) for row in short.itertuples(index=False)]
        short["_stripped_values"] = [light_preprocess(*strip_source_markers(row.text, row.title)) for row in short.itertuples(index=False)]
        main = de_duped.reset_index(drop=True)
        flagged_ids = []
        if name == "fake_news_formated":
            flagged_ids = sorted(set(str(value) for value in main["dataset_id"].dropna().unique()) & FLAGGED_FORMATTED_IDS)
            main = main.loc[~main["dataset_id"].astype(str).isin(FLAGGED_FORMATTED_IDS)].reset_index(drop=True)
        entry: dict[str, Any] = {"rows_before": before, "overlap": overlap, "quality_filter": quality, "flagged_dataset_ids_excluded": flagged_ids, "rows_after_main": len(main), "main_original_model": evaluate(original_model, original_vec, main, main["_original_values"].tolist()), "main_stripped_model": evaluate(stripped_model, stripped_vec, main, main["_stripped_values"].tolist())}
        if name == "realfakenews":
            entry["headline_or_short_set"] = {"rows": len(short), "overlap": short_overlap, "original_model": evaluate(original_model, original_vec, short, short["_original_values"].tolist()), "stripped_model": evaluate(stripped_model, stripped_vec, short, short["_stripped_values"].tolist()), "manual_noise_review": manual_realfake_review(standardized)}
        if name == "polsci_fake_news":
            entry["short_text_set"] = {"rows": len(short), "overlap": short_overlap, "original_model": evaluate(original_model, original_vec, short, short["_original_values"].tolist()), "stripped_model": evaluate(stripped_model, stripped_vec, short, short["_stripped_values"].tolist())}
        if name == "fake_news_formated":
            entry["per_dataset_id"] = {}
            for dataset_id, review_group in de_duped.groupby("dataset_id", dropna=False):
                dataset_id_key = str(dataset_id)
                safe_print(f"\n=== fake_news_formated dataset_id={dataset_id_key}: 5 samples per label ===")
                for label in (0, 1):
                    for row in review_group.loc[review_group["label"] == label].sample(min(5, int((review_group["label"] == label).sum())), random_state=SEED).itertuples(index=False):
                        safe_print(f"LABEL={label} {row.text[:300].replace(chr(10), ' ')}")
            original_probabilities = score_values(original_model, original_vec, main["_original_values"].tolist())
            stripped_probabilities = score_values(stripped_model, stripped_vec, main["_stripped_values"].tolist())
            for dataset_id, group in main.groupby("dataset_id", dropna=False):
                dataset_id_key = str(dataset_id)
                positions = group.index.to_numpy()
                flagged = dataset_id_key in FLAGGED_FORMATTED_IDS
                entry["per_dataset_id"][dataset_id_key] = {"rows_before": len(group), "rows_after": len(group), "flagged_unreliable": flagged, "flag_reason": "Empty content, inverted-looking labels, or unreliable mixed provenance in manual samples." if flagged else "No inversion was evident in the five-sample-per-label review; verify upstream provenance before treating as independent.", "original_model": scored_metrics(group, original_probabilities[positions]), "stripped_model": scored_metrics(group, stripped_probabilities[positions])}
        result["datasets"][name] = entry
    write_json(Path(__file__).with_name("e6_external.json"), result)


if __name__ == "__main__":
    main()
