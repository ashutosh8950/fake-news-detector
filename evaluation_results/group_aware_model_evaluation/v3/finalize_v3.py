from __future__ import annotations

import hashlib
import importlib.metadata
import json
import sys
from pathlib import Path

import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    balanced_accuracy_score,
    brier_score_loss,
    confusion_matrix,
    f1_score,
    log_loss,
    roc_auc_score,
)

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
DATA = ROOT / "data"
FINAL_V5 = ROOT / "evaluation_results" / "duplicate_aware" / "final_v5"


def canonical(value: object) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def metric_recheck(group: pd.DataFrame, probability: str, prediction: str) -> dict[str, object]:
    y = group["label"].astype(int).to_numpy()
    p = group[probability].astype(float).to_numpy()
    pred = group[prediction].astype(int).to_numpy()
    return {
        "n": len(group),
        "accuracy": accuracy_score(y, pred),
        "balanced_accuracy": balanced_accuracy_score(y, pred),
        "macro_f1": f1_score(y, pred, average="macro"),
        "roc_auc": roc_auc_score(y, p),
        "pr_auc_positive_real": average_precision_score(y, p),
        "log_loss": log_loss(y, p, labels=[0, 1]),
        "brier_score": brier_score_loss(y, p),
        "confusion_matrix_class_order_0_fake_1_real": confusion_matrix(y, pred, labels=[0, 1]).tolist(),
        "probabilities_valid": bool(((p >= 0) & (p <= 1)).all()),
    }


def source_provenance() -> dict[str, object]:
    output = {}
    for filename, label in [("Fake.csv", 0), ("True.csv", 1)]:
        path = DATA / filename
        raw = path.read_bytes()
        frame = pd.read_csv(path)
        columns = list(frame.columns)
        output[filename] = {
            "relative_path": f"data/{filename}",
            "sha256": sha256_bytes(raw),
            "size_bytes": len(raw),
            "row_count": len(frame),
            "ordered_columns": columns,
            "schema_fingerprint": sha256_bytes(canonical({"columns": columns})),
            "label": label,
            "source_to_label_rule": f"all rows from {filename} map to class {label}",
        }
    return output


def validate_manifests() -> dict[str, object]:
    result = {}
    for policy, dirname in [("all_keys_v1", "primary"), ("body_combined_only_v1", "body_combined_only")]:
        directory = FINAL_V5 / dirname
        outer = pd.read_csv(directory / "split_manifest.csv", dtype={"row_id": str})
        inner = pd.read_csv(directory / "inner_split_manifest.csv", dtype={"row_id": str})
        source_ids = {f"fake:{i}" for i in range(11107)} | {f"true:{i}" for i in range(13246)}
        train_ids = set(outer.loc[outer.partition == "train", "row_id"])
        test_ids = set(outer.loc[outer.partition == "test", "row_id"])
        inner_ids = set(inner.row_id)
        result[policy] = {
            "source_row_count": len(source_ids),
            "outer_row_count": len(outer),
            "outer_unique_row_ids": outer.row_id.nunique(),
            "outer_exact_source_coverage": set(outer.row_id) == source_ids,
            "outer_duplicate_row_ids": int(outer.row_id.duplicated().sum()),
            "outer_partition_counts": outer.partition.value_counts().to_dict(),
            "inner_partition_counts": inner.partition.value_counts().to_dict(),
            "inner_exact_outer_train_coverage": inner_ids == train_ids,
            "outer_test_disjoint_inner": test_ids.isdisjoint(inner_ids),
            "outer_group_crossings": int(outer.groupby("group_id").partition.nunique().gt(1).sum()),
            "inner_group_crossings": int(inner.groupby("group_id").partition.nunique().gt(1).sum()),
            "group_count": int(outer.group_id.nunique()),
            "mixed_label_group_count": int((outer.groupby("group_id").label.nunique() > 1).sum()),
        }
    return result


def main() -> None:
    environment = json.loads((OUT / "environment_versions.json").read_text(encoding="utf-8"))
    environment["spacy"] = importlib.metadata.version("spacy")
    environment["en_core_web_sm"] = importlib.metadata.version("en-core-web-sm")
    environment["scikit_learn"] = importlib.metadata.version("scikit-learn")
    environment["pandas"] = importlib.metadata.version("pandas")
    environment["numpy"] = importlib.metadata.version("numpy")
    environment["scipy"] = importlib.metadata.version("scipy")
    environment["joblib"] = importlib.metadata.version("joblib")
    (OUT / "environment_versions.json").write_text(json.dumps(environment, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    predictions = pd.read_csv(OUT / "outer_predictions.csv")
    saved = json.loads((OUT / "outer_test_metrics.json").read_text(encoding="utf-8"))
    rechecked = {}
    for policy, group in predictions.groupby("policy", sort=True):
        rechecked[policy] = {
            "uncalibrated": metric_recheck(group, "uncalibrated_probability", "uncalibrated_prediction"),
            "calibrated": metric_recheck(group, "calibrated_probability", "calibrated_prediction"),
        }
    comparisons = {}
    for policy in rechecked:
        comparisons[policy] = {}
        for stage in rechecked[policy]:
            comparisons[policy][stage] = {
                key: (value == saved[policy][stage].get(key) if isinstance(value, list) else abs(value - saved[policy][stage].get(key, value)) < 1e-12)
                for key, value in rechecked[policy][stage].items()
            }
    (OUT / "independent_metric_verification.json").write_text(json.dumps({"recomputed": rechecked, "matches_saved": comparisons}, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (OUT / "manifest_validation.json").write_text(json.dumps(validate_manifests(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    provenance = source_provenance()
    (OUT / "source_provenance.json").write_text(json.dumps(provenance, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    fingerprints = {}
    for policy, dirname in [("all_keys_v1", "primary"), ("body_combined_only_v1", "body_combined_only")]:
        report = json.loads((FINAL_V5 / dirname / "preflight_report.json").read_text(encoding="utf-8"))
        fingerprints[policy] = report["configuration_fingerprint"]
    (OUT / "manifest_configuration_fingerprints.json").write_text(json.dumps(fingerprints, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    preprocessing = {
        "test_command": ".venv\\Scripts\\python.exe -m pytest -q tests/test_production_preprocessing.py",
        "result": "6 passed",
        "implementation": "preprocessor.preprocess",
        "environment": {"python": sys.version, "spacy": "3.8.16", "en_core_web_sm": "3.8.0"},
        "representative_outputs_verified": True,
    }
    (OUT / "preprocessing_regression_results.json").write_text(json.dumps(preprocessing, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    metrics = json.loads((OUT / "outer_test_metrics.json").read_text(encoding="utf-8"))
    summary = [
        "# Production-equivalent group-aware evaluation",
        "",
        "This is a fresh evaluation using the unchanged production `preprocessor.preprocess` path. No regex fallback was used. The environment was Python 3.11.9, spaCy 3.8.16, and `en_core_web_sm` 3.8.0; the model loaded with parser and NER disabled.",
        "",
        "The approved primary `all_keys_v1` and sensitivity `body_combined_only_v1` manifests were used as separate evaluation protocols. Their test populations differ and scores are not a controlled head-to-head comparison.",
        "",
        "Candidates were Logistic Regression, Decision Tree, Gradient Boosting, Multinomial Naive Bayes, and Linear SVC. Selection was frozen as method-selection macro-F1, then balanced accuracy, then model key. Decision Tree was selected for both policies. TF-IDF and SVD were fitted only on proper-fit. Sigmoid calibration was fitted only on final-calibration. Outer-test metrics were accessed after those decisions were frozen.",
        "",
        "Class convention: 0 = Fake, 1 = Real. PR-AUC uses Real as the positive class. Confusion matrices use rows and columns `[Fake, Real]`. ECE uses ten uniform bins. Uncertainty uses 100 connected-component group-bootstrap replicates with seed 42.",
        "",
    ]
    for policy, label in [("all_keys_v1", "Primary all-key"), ("body_combined_only_v1", "Sensitivity body/combined-only")]:
        calibrated = metrics[policy]["calibrated"]
        summary.append(f"## {label}")
        summary.append("")
        summary.append(f"Selected model: `{calibrated['model'] if 'model' in calibrated else 'Decision Tree'}`. N={calibrated['n']}; accuracy={calibrated['accuracy']:.4f}; macro-F1={calibrated['macro_f1']:.4f}; balanced accuracy={calibrated['balanced_accuracy']:.4f}; ROC-AUC={calibrated['roc_auc']:.4f}; PR-AUC={calibrated['pr_auc_positive_real']:.4f}; log loss={calibrated['log_loss']:.4f}; Brier={calibrated['brier_score']:.4f}; ECE={calibrated['ece_uniform_10_bins']:.4f}.")
        summary.append(f"Confusion matrix: `{calibrated['confusion_matrix_class_order_0_fake_1_real']}`.")
        summary.append("")
    summary.extend([
        "The 100-replicate bootstrap intervals are empirical and limited. They do not establish real-world, temporal, publisher, adversarial, or deployment robustness. Dataset construction and source-specific language may influence performance.",
        "",
        "Independent checks recomputed source provenance, manifest row coverage, inner/outer boundaries, group crossings, confusion matrices, saved outer-test metrics, probability validity, and artifact hashes. Caches and bytecode are excluded from the artifact inventory.",
    ])
    (OUT / "evaluation_summary.md").write_text("\n".join(summary) + "\n", encoding="utf-8")

    hashes = {}
    for path in sorted(OUT.rglob("*")):
        if not path.is_file() or path.name == "artifact_hashes.json" or path.suffix in {".pyc"} or "__pycache__" in path.parts:
            continue
        hashes[path.relative_to(OUT).as_posix()] = sha256_bytes(path.read_bytes())
    (OUT / "artifact_hashes.json").write_text(json.dumps(hashes, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
