"""E6: evaluate the audit models on external, non-production datasets.

Downloads are temporary and are never written under experiments/phase_b.
"""

from __future__ import annotations

import tempfile
from pathlib import Path

import numpy as np
import pandas as pd
import requests

from common import ensemble_predictions, fit_models, light_preprocess, load_grouped_data, preprocess_rows, classification_metrics, write_json
from run_e3_marker_stripping import strip_source_markers


DATASETS = {
    "polsci_fake_news": {
        "repo": "polsci/fake-news",
        "url": "https://huggingface.co/datasets/polsci/fake-news",
        "license": "GPL (dataset card; verify upstream terms before redistribution)",
        "caveat": "480 short legitimate/fake examples; not article-length and label semantics are crowdsourced/web-source based.",
    },
    "realfakenews": {
        "repo": "fauxNeuz/RealFakeNews",
        "url": "https://huggingface.co/datasets/fauxNeuz/RealFakeNews",
        "license": "CC BY-NC-SA 4.0",
        "caveat": "108,032 samples; non-commercial/share-alike license and mixed source/region composition.",
    },
    "fake_news_formated": {
        "repo": "magnea/fake-news-formated",
        "url": "https://huggingface.co/datasets/magnea/fake-news-formated",
        "license": "Apache-2.0 (dataset card)",
        "caveat": "165,620 rows aggregated from multiple upstream datasets; dataset_id must be treated as a provenance caveat, not an independent source guarantee.",
    },
}
MANUAL_DIR = Path(__file__).with_name("external")


def download_frame(name: str, spec: dict[str, str], directory: Path) -> pd.DataFrame:
    manual = MANUAL_DIR / f"{name}.parquet"
    if manual.exists():
        return pd.read_parquet(manual)
    response = requests.get(
        "https://datasets-server.huggingface.co/parquet",
        params={"dataset": spec["repo"]},
        timeout=60,
    )
    response.raise_for_status()
    files = response.json()["parquet_files"]
    if not files:
        raise RuntimeError(f"No Parquet file was advertised for {name}")
    local = directory / f"{name}.parquet"
    with requests.get(files[0]["url"], stream=True, timeout=300) as download:
        download.raise_for_status()
        with local.open("wb") as handle:
            for chunk in download.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    handle.write(chunk)
    return pd.read_parquet(local)


def normalize(value: object) -> str:
    return " ".join("".join(char.lower() if char.isalnum() else " " for char in str(value)).split())


def standardize(name: str, frame: pd.DataFrame) -> pd.DataFrame:
    columns = {str(column).lower(): column for column in frame.columns}
    text_column = columns.get("text") or columns.get("content")
    title_column = columns.get("title")
    label_column = columns.get("label") or columns.get("classification")
    if not text_column or not label_column:
        raise ValueError(f"{name} lacks text/label columns: {list(frame.columns)}")
    result = pd.DataFrame({"title": frame[title_column] if title_column else "", "text": frame[text_column], "raw_label": frame[label_column]})
    result["title"] = result["title"].fillna("").astype(str)
    result["text"] = result["text"].fillna("").astype(str)
    labels = result["raw_label"].astype(str).str.lower()
    result["label"] = labels.map({"real": 1, "legit": 1, "true": 1, "1": 1, "fake": 0, "false": 0, "0": 0})
    result = result.dropna(subset=["label"]).copy()
    result["label"] = result["label"].astype(int)
    return result[["title", "text", "label"]].reset_index(drop=True)


def evaluate(models, vec, frame: pd.DataFrame, stripped: bool) -> dict[str, object]:
    values = []
    for row in frame.itertuples(index=False):
        title, text = (strip_source_markers(row.text, row.title) if stripped else (row.title, row.text))
        values.append(light_preprocess(title, text))
    probabilities, predictions = ensemble_predictions(models, vec, values)
    metrics = classification_metrics(frame["label"].to_numpy(dtype=int), predictions, probabilities)
    return {
        "accuracy": metrics["accuracy"],
        "fake_recall": metrics["per_class"]["fake"]["recall"],
        "real_recall": metrics["per_class"]["real"]["recall"],
        "roc_auc": metrics["roc_auc"],
        "percent_predicted_fake": float((predictions == 0).mean() * 100.0),
        "rows_evaluated": len(frame),
    }


def main() -> None:
    train, _, all_data = load_grouped_data()
    training_keys = set((normalize(row.title), normalize(row.text)) for row in all_data.itertuples(index=False))
    original_train = preprocess_rows(train, light=True)
    stripped_train = [light_preprocess(*strip_source_markers(row.text, row.title)) for row in train.itertuples(index=False)]
    original_vec, original_models = fit_models(original_train, train["label"])
    stripped_vec, stripped_models = fit_models(stripped_train, train["label"])
    result = {"experiment": "E6", "datasets": {}}
    with tempfile.TemporaryDirectory(prefix="phase-b-external-") as temp:
        temp_dir = Path(temp)
        try:
            for name, spec in DATASETS.items():
                raw = download_frame(name, spec, temp_dir)
                frame = standardize(name, raw)
                before = len(frame)
                keys = [(normalize(row.title), normalize(row.text)) for row in frame.itertuples(index=False)]
                frame = frame.loc[[key not in training_keys for key in keys]].reset_index(drop=True)
                result["datasets"][name] = {
                    "source_url": spec["url"], "license": spec["license"], "size_downloaded": before,
                    "duplicates_removed": before - len(frame),
                    "label_mapping": "real/legit/true/1 -> 1; fake/false/0 -> 0",
                    "caveat": spec["caveat"],
                    "original_model": evaluate(original_models, original_vec, frame, False),
                    "stripped_model": evaluate(stripped_models, stripped_vec, frame, True),
                }
        except requests.RequestException as exc:
            result["status"] = "NOT FOUND"
            result["reason"] = f"Dataset download blocked: {exc}"
            result["manual_downloads"] = {
                name: str(MANUAL_DIR / f"{name}.parquet") for name in DATASETS
            }
    write_json(Path(__file__).with_name("e6_external.json"), result)


if __name__ == "__main__":
    main()
