"""Tasks 1-3: ISOT-style markers, train-only TF-IDF similarity, and plot."""
from __future__ import annotations

import json
from pathlib import Path
import re

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import NearestNeighbors

from common import load_grouped_data
from run_e6_external import DATASETS, EXTERNAL, FLAGGED_FORMATTED_IDS, first_300_words, normalize_body

BASE = Path(__file__).with_name("e6_external.json")
OUT = Path(__file__).with_name("e6_similarity_analysis.json")
CSV_OUT = Path(__file__).with_name("e6_similarity_table.csv")
PATTERN_OUT = Path(__file__).with_name("e6_pattern_comparison.csv")
FIGURE = Path(__file__).with_name("figures") / "e6_similarity_vs_accuracy.png"


def patterns(texts: pd.Series) -> dict[str, float]:
    values = texts.fillna("").astype(str)
    checks = {"reuters_parenthetical": r"\(\s*Reuters\s*\)", "reuters_dateline": r"^[A-Z][A-Z .,'/-]{2,40}\s+\(Reuters\)\s*[-:–—]", "isot_apostrophe_stripped": r"\b(?:it s|can t|don t|doesn t|isn t|wasn t|wouldn t|couldn t|shouldn t)\b"}
    return {name: float(values.str.contains(pattern, case=False, regex=True, na=False).mean() * 100) for name, pattern in checks.items()}


def english(text: str) -> bool:
    words = set(re.findall(r"[a-z]+", text.lower()))
    ascii_ratio = sum(char.isascii() for char in text if char.isalpha()) / max(sum(char.isalpha() for char in text), 1)
    return ascii_ratio >= 0.85 and len(words & {"the", "and", "that", "this", "with", "from", "have", "for", "are", "was", "said"}) >= 3


def cleaned(raw: pd.DataFrame, text_col: str, iso_exact: set[str]) -> pd.DataFrame:
    frame = pd.DataFrame({"text": raw[text_col].fillna("").astype(str)})
    frame["label"] = raw["classification"] if "classification" in raw else raw["label"]
    if "dataset_id" in raw:
        frame["dataset_id"] = raw["dataset_id"]
    mask = frame["text"].str.strip().ne("") & frame["text"].map(english) & frame["text"].str.len().ge(300)
    return frame.loc[mask & ~frame["text"].map(normalize_body).isin(iso_exact)].reset_index(drop=True)


def similarity(frame: pd.DataFrame, vectorizer: TfidfVectorizer, centroid: np.ndarray, nearest: NearestNeighbors) -> tuple[float, float]:
    if frame.empty:
        return float("nan"), float("nan")
    texts = frame["text"].map(first_300_words).tolist()
    means, above = [], []
    for start in range(0, len(texts), 500):
        matrix = vectorizer.transform(texts[start : start + 500])
        means.extend(np.asarray(matrix @ centroid).ravel())
        distances, _ = nearest.kneighbors(matrix, n_neighbors=1)
        above.extend((1.0 - distances[:, 0]) > 0.5)
    return float(np.mean(means)), float(np.mean(above) * 100)


def main() -> None:
    train, _, all_data = load_grouped_data()
    iso_exact = set(all_data["text"].map(normalize_body))
    vectorizer = TfidfVectorizer(ngram_range=(1, 2), min_df=2, max_features=10_000, stop_words="english")
    train_matrix = vectorizer.fit_transform(train["text"].map(first_300_words))
    centroid = np.asarray(train_matrix.mean(axis=0)).ravel()
    centroid /= max(float(np.linalg.norm(centroid)), 1e-12)
    sampled = train.sample(min(5000, len(train)), random_state=42)
    sampled_matrix = vectorizer.transform(sampled["text"].map(first_300_words))
    nearest = NearestNeighbors(n_neighbors=1, metric="cosine", n_jobs=1).fit(sampled_matrix)
    metrics = json.loads(BASE.read_text(encoding="utf-8"))["datasets"]
    pattern_rows = [{"subset": "ISOT train", **patterns(train["text"])}, {"subset": "ISOT all", **patterns(all_data["text"])}]
    rows = []
    for name, spec in DATASETS.items():
        raw = pd.read_parquet(EXTERNAL / spec["file"])
        pattern_rows.append({"subset": name, **patterns(raw[spec["text"]])})
        frame = cleaned(raw, spec["text"], iso_exact)
        subsets = {name: frame}
        if name == "realfakenews":
            short = raw.loc[raw[spec["text"]].fillna("").astype(str).str.len().lt(300)].copy()
            short["text"] = short[spec["text"]].fillna("").astype(str)
            subsets["realfakenews_short"] = short.loc[~short["text"].map(normalize_body).isin(iso_exact)].reset_index(drop=True)
            pattern_rows.append({"subset": "realfakenews_short", **patterns(subsets["realfakenews_short"]["text"])})
        if name == "fake_news_formated":
            subsets = {f"fake_news_formated_id_{did}": frame.loc[frame["dataset_id"].astype(str) == str(did)].copy() for did in [float(i) for i in range(9)]}
        for subset_name, subset in subsets.items():
            sim_mean, sim_share = similarity(subset, vectorizer, centroid, nearest)
            source = metrics[name]
            if subset_name == "realfakenews_short":
                source = source["headline_or_short_set"]
            elif subset_name.startswith("fake_news_formated_id_"):
                source = source["per_dataset_id"].get(subset_name.rsplit("_", 1)[-1], {}).get("original_model", {})
            else:
                source = source.get("main_original_model", {})
            rows.append({"subset": subset_name, "clean_rows": len(subset), "accuracy": source.get("accuracy"), "roc_auc": source.get("roc_auc"), "fake_recall": source.get("fake_recall"), "real_recall": source.get("real_recall"), "percent_predicted_fake": source.get("percent_predicted_fake"), "mean_tfidf_cosine_to_isot_train_centroid": sim_mean, "nearest_isot_cosine_gt_0_5_percent": sim_share, "flagged_unreliable": subset_name.startswith("fake_news_formated_id_") and subset_name.rsplit("_", 1)[-1] in FLAGGED_FORMATTED_IDS})
    table = pd.DataFrame(rows)
    valid = table.dropna(subset=["accuracy", "roc_auc", "mean_tfidf_cosine_to_isot_train_centroid"])
    correlations = {"pearson_similarity_accuracy": float(np.corrcoef(valid["mean_tfidf_cosine_to_isot_train_centroid"], valid["accuracy"])[0, 1]), "pearson_similarity_auc": float(np.corrcoef(valid["mean_tfidf_cosine_to_isot_train_centroid"], valid["roc_auc"])[0, 1])}
    FIGURE.parent.mkdir(parents=True, exist_ok=True)
    plt.figure(figsize=(7, 4.5))
    plt.scatter(valid["mean_tfidf_cosine_to_isot_train_centroid"], valid["accuracy"], label="Accuracy")
    plt.scatter(valid["mean_tfidf_cosine_to_isot_train_centroid"], valid["roc_auc"], marker="x", label="ROC-AUC")
    for _, row in valid.iterrows():
        plt.annotate(row["subset"].replace("fake_news_formated_", "fmt_"), (row["mean_tfidf_cosine_to_isot_train_centroid"], row["accuracy"]), fontsize=6)
    plt.xlabel("Mean TF-IDF cosine to ISOT train centroid")
    plt.ylabel("Score")
    plt.title("External performance versus ISOT similarity")
    plt.legend(); plt.tight_layout(); plt.savefig(FIGURE, dpi=150); plt.close()
    table.to_csv(CSV_OUT, index=False); pd.DataFrame(pattern_rows).to_csv(PATTERN_OUT, index=False)
    rf = pd.read_parquet(EXTERNAL / "realfakenews.parquet")
    output = {"experiment": "E6 Tasks 1-3", "pattern_comparison": pattern_rows, "similarity_accuracy_table": rows, "correlations": correlations, "nearest_neighbor_method": "nearest cosine neighbour among fixed random_state=42 sample of 5,000 ISOT train rows; centroid uses all ISOT train rows", "reuters_label_crosstab": pd.crosstab(rf["label"], rf["text"].astype(str).str.contains(r"\(Reuters\)", case=False, regex=True)).to_dict(), "figure": str(FIGURE)}
    OUT.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(table.to_string(index=False)); print("correlations", correlations)


if __name__ == "__main__":
    main()
