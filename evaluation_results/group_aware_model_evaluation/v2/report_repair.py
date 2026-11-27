"""Package and independently verify the v1 fallback evaluation without retraining."""

from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path

import pandas as pd
from sklearn.metrics import confusion_matrix


ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT / "data"
V1 = ROOT / "evaluation_results" / "group_aware_model_evaluation" / "v1"
OUT = Path(__file__).resolve().parent


def canonical_json(value: object) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def source_provenance() -> dict[str, object]:
    result = {}
    for filename, label, source_name in [("Fake.csv", 0, "fake"), ("True.csv", 1, "true")]:
        path = SOURCE / filename
        raw = path.read_bytes()
        frame = pd.read_csv(path)
        columns = list(frame.columns)
        result[filename] = {
            "relative_path": f"data/{filename}",
            "sha256": sha256_bytes(raw),
            "size_bytes": len(raw),
            "row_count": int(len(frame)),
            "ordered_columns": columns,
            "schema_fingerprint": sha256_bytes(canonical_json({"columns": columns})),
            "label": label,
            "source_to_label_rule": f"all rows from {filename} map to class {label} ({'Fake' if label == 0 else 'Real'})",
            "source_name": source_name,
        }
    return result


def repair_confusion_matrices(predictions: pd.DataFrame, metrics: dict[str, object]) -> dict[str, object]:
    repaired = {}
    for policy, group in predictions.groupby("policy", sort=True):
        repaired[policy] = {}
        for stage, prediction_column in (
            ("uncalibrated", "uncalibrated_prediction"),
            ("calibrated", "calibrated_prediction"),
        ):
            matrix = confusion_matrix(group["label"], group[prediction_column], labels=[0, 1]).tolist()
            expected = metrics[policy][stage]["confusion_matrix_class_order_0_fake_1_real"]
            if matrix != expected:
                raise AssertionError(f"matrix mismatch for {policy}/{stage}: {matrix} != {expected}")
            repaired[policy][stage] = {
                "axis_order": ["Fake", "Real"],
                "class_order": [0, 1],
                "matrix": matrix,
            }
    return repaired


def copy_meaningful_v1_outputs() -> None:
    excluded = {"source_provenance.json", "confusion_matrices.json", "artifact_hashes.json"}
    for path in V1.iterdir():
        if path.name in excluded or path.name == "__pycache__" or not path.is_file():
            continue
        shutil.copy2(path, OUT / path.name)


def main() -> None:
    if not V1.is_dir():
        raise FileNotFoundError(V1)
    copy_meaningful_v1_outputs()
    predictions = pd.read_csv(V1 / "outer_predictions.csv")
    metrics = json.loads((V1 / "outer_test_metrics.json").read_text(encoding="utf-8"))
    provenance = source_provenance()
    v1_provenance = json.loads((V1 / "source_provenance.json").read_text(encoding="utf-8"))
    for filename, record in provenance.items():
        if record["sha256"] != v1_provenance[filename]["sha256"]:
            raise RuntimeError(f"source hash differs from v1 for {filename}")

    matrices = repair_confusion_matrices(predictions, metrics)
    (OUT / "source_provenance.json").write_text(json.dumps(provenance, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (OUT / "confusion_matrices.json").write_text(
        json.dumps(
            {
                "axis_order": ["Fake", "Real"],
                "positive_class": 1,
                "positive_class_name": "Real",
                "policies": matrices,
                "independent_recomputation": True,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    (OUT / "production_preflight.json").write_text(
        json.dumps(
            {
                "production_equivalent_rerun": "blocked",
                "spacy_installed": False,
                "en_core_web_sm_available": False,
                "reason": "The active Python environment has no importable spacy package; no dependency installation or model download was attempted.",
                "production_preprocessor": "preprocessor.py requires spacy.load('en_core_web_sm') at module import.",
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    summary = """# Group-aware model evaluation — corrected v1 report package

This namespace packages the existing Task 10 evaluation; it does not retrain models.
The experiment used the explicitly documented `regex_fallback_experimental` preprocessing because the active environment has no importable `spacy` package and no `en_core_web_sm` model. It is therefore not production-equivalent.

The primary `all_keys_v1` and sensitivity `body_combined_only_v1` policies use distinct approved test populations. The candidates were Logistic Regression, Decision Tree, Gradient Boosting, Multinomial Naive Bayes, and Linear SVC. Selection used method-selection macro-F1, with balanced accuracy and model key as tie-breakers. Decision Tree was selected for both policies. A fixed sigmoid calibrator was fitted only on `final_calibration`; outer-test metrics were then computed once.

Metrics use class 0 = Fake and class 1 = Real. PR-AUC treats Real as positive. Confusion matrices use rows and columns in `[Fake, Real]` order. The saved predictions independently reproduce the metrics in `outer_test_metrics.json`, and the matrices in this namespace were independently reconstructed from those predictions.

Primary calibrated outer-test results: accuracy 0.9647, macro-F1 0.9645, balanced accuracy 0.9654, ROC-AUC 0.9654, PR-AUC 0.9588, log loss 0.1551, Brier score 0.0342, ECE 0.0134; matrix `[[1622, 44], [85, 1902]]`.

Sensitivity calibrated outer-test results: accuracy 0.9766, macro-F1 0.9765, balanced accuracy 0.9765, ROC-AUC 0.9765, PR-AUC 0.9697, log loss 0.1107, Brier score 0.0228, ECE 0.00135; matrix `[[1576, 40], [43, 1894]]`.

Uncertainty uses 100 group-bootstrap replicates with seed 42 and connected-component groups as the resampling unit. This is a limited empirical interval, not a guarantee. The two policies are not a controlled head-to-head comparison because their grouping rules and test populations differ. Dataset-specific language, source construction, temporal effects, publisher effects, and adversarial generalization remain unresolved.

Task 10 identified a serialization bug: the original writer requested `confusion_matrix` while the metric object stored `confusion_matrix_class_order_0_fake_1_real`, producing null values. This package reconstructs the matrices from saved prediction labels and verifies equality with the saved metrics. Source bytes, row counts, ordered schemas, labels, and schema fingerprints were independently recomputed.

Production-equivalent retraining is blocked pending installation and validation of the required spaCy package and `en_core_web_sm` model. No installation or download was attempted.
"""
    (OUT / "evaluation_summary.md").write_text(summary, encoding="utf-8")

    excluded_suffixes = {".pyc"}
    hashes = {}
    for path in sorted(OUT.rglob("*")):
        if not path.is_file() or path.name == "artifact_hashes.json" or path.suffix in excluded_suffixes or "__pycache__" in path.parts:
            continue
        hashes[str(path.relative_to(OUT)).replace("\\", "/")] = sha256_bytes(path.read_bytes())
    (OUT / "artifact_hashes.json").write_text(json.dumps(hashes, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
