"""Run the canonical calibrated five-model production pipeline.

The split is taken from the checked-in duplicate-aware manifest. Model fitting
and calibration are delegated to ``phase2_calibration`` so this command keeps
the production hyperparameters and preprocessing in one place.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import (
    brier_score_loss,
    classification_report,
    confusion_matrix,
    roc_auc_score,
)

import phase2_calibration
from artifact_contract import sha256_file
from scripts.build_manifest import build_manifest

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
RESULTS_DIR = ROOT / "evaluation_results"
HELD_OUT_PATH = RESULTS_DIR / "held_out_test_set.csv"
PREDICTIONS_PATH = RESULTS_DIR / "production_predictions.csv"
METRICS_PATH = RESULTS_DIR / "production_metrics_report.json"
MANIFEST_PATH = ROOT / "models" / "calibrated" / "artifact_manifest.json"


def _manifest_path() -> Path:
    candidates = [
        RESULTS_DIR / "duplicate_aware" / "final_v5" / "primary" / "split_manifest.csv",
        ROOT / "docs" / "audit_archive" / "duplicate_aware" / "final_v5" / "primary" / "split_manifest.csv",
    ]
    for path in candidates:
        if path.is_file():
            return path
    raise FileNotFoundError("No duplicate-aware primary split manifest was found")


def _load_duplicate_aware_split() -> tuple[pd.DataFrame, pd.DataFrame, Path]:
    manifest_path = _manifest_path()
    manifest = pd.read_csv(manifest_path)
    fake = pd.read_csv(DATA_DIR / "Fake.csv")
    true = pd.read_csv(DATA_DIR / "True.csv")
    frames = []
    for source_file, frame, label in (("Fake.csv", fake, 0), ("True.csv", true, 1)):
        frame = frame.copy()
        frame["class"] = label
        frame["row_id"] = [f"{'fake' if label == 0 else 'true'}:{i}" for i in range(len(frame))]
        frame["source_file"] = source_file
        frame["source_ordinal"] = np.arange(len(frame))
        frames.append(frame)
    data = pd.concat(frames, ignore_index=True)
    joined = data.merge(manifest[["row_id", "partition", "group_id"]], on="row_id", how="left", validate="one_to_one")
    if joined["partition"].isna().any():
        raise ValueError("Split manifest does not cover every dataset row")
    if joined.groupby("group_id")["partition"].nunique().gt(1).any():
        raise ValueError("A duplicate-aware group crosses train/test partitions")
    held_out = joined.loc[joined["partition"] == "test", ["title", "text", "class"]].copy()
    train = joined.loc[joined["partition"] == "train", ["title", "text", "class"]].copy()
    if len(train) != 20700 or len(held_out) != 3653:
        raise ValueError(f"Expected 20,700/3,653 rows, got {len(train)}/{len(held_out)}")
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    held_out.to_csv(HELD_OUT_PATH, index=False)
    return train, held_out, manifest_path


def _ece(labels: np.ndarray, probabilities: np.ndarray, bins: int = 10) -> float:
    edges = np.linspace(0.0, 1.0, bins + 1)
    total = 0.0
    for low, high in zip(edges[:-1], edges[1:]):
        mask = (probabilities >= low) & ((probabilities < high) if high < 1.0 else (probabilities <= high))
        if mask.any():
            total += float(mask.mean()) * abs(float(labels[mask].mean()) - float(probabilities[mask].mean()))
    return round(total, 6)


def _write_metrics(held_out: pd.DataFrame, manifest_path: Path) -> None:
    report = json.loads((RESULTS_DIR / "phase2_calibration_report.json").read_text(encoding="utf-8"))
    report["production_switch"] = True
    (RESULTS_DIR / "phase2_calibration_report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    import joblib

    from artifact_contract import extract_real_probability
    from preprocessor import preprocess

    vectorizer = joblib.load(ROOT / "models" / "calibrated" / "vectorizer.pkl")
    models = {
        key: joblib.load(ROOT / "models" / "calibrated" / f"{key}_calibrated.pkl")
        for key in phase2_calibration.MODEL_NAMES
    }
    features = vectorizer.transform([preprocess(row.title, row.text) for row in held_out.itertuples(index=False)])
    probabilities = np.vstack([
        [extract_real_probability(model, features[i]) for i in range(features.shape[0])]
        for model in models.values()
    ]).mean(axis=0)
    labels = held_out["class"].to_numpy(dtype=int)
    predictions = (probabilities >= 0.5).astype(int)
    pd.DataFrame({"label": labels, "real_probability": probabilities, "prediction": predictions}).to_csv(PREDICTIONS_PATH, index=False)
    classes = classification_report(labels, predictions, labels=[0, 1], target_names=["fake", "real"], output_dict=True, zero_division=0)
    metrics = {
        "split_manifest": str(manifest_path.relative_to(ROOT)),
        "split_manifest_sha256": sha256_file(manifest_path),
        "rows": len(labels),
        "accuracy": float((predictions == labels).mean()),
        "per_class": {key: classes[key] for key in ("fake", "real")},
        "confusion_matrix_class_order_0_fake_1_real": confusion_matrix(labels, predictions, labels=[0, 1]).tolist(),
        "roc_auc_positive_class_real": float(roc_auc_score(labels, probabilities)),
        "brier_score": float(brier_score_loss(labels, probabilities)),
        "ece_uniform_10_bins": _ece(labels, probabilities),
        "predictions_file": str(PREDICTIONS_PATH.relative_to(ROOT)),
    }
    METRICS_PATH.write_text(json.dumps(metrics, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    train, held_out, manifest_path = _load_duplicate_aware_split()
    print(f"Using {manifest_path}")
    print(f"Duplicate-aware split: {len(train)} train / {len(held_out)} test")
    phase2_calibration.main()
    build_manifest(ROOT / "models" / "calibrated", RESULTS_DIR / "phase2_calibration_report.json", MANIFEST_PATH)
    _write_metrics(held_out, manifest_path)
    print(f"Wrote {METRICS_PATH}")
    print(f"Wrote {PREDICTIONS_PATH}")


if __name__ == "__main__":
    main()
