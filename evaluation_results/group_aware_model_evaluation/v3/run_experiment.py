from __future__ import annotations

import csv
import hashlib
import json
import math
import platform
import re
import sys
import time
import warnings
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
import pandas as pd
import sklearn
import spacy
ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from preprocessor import preprocess
from sklearn.decomposition import TruncatedSVD
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    balanced_accuracy_score,
    brier_score_loss,
    confusion_matrix,
    f1_score,
    log_loss,
    precision_recall_fscore_support,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.naive_bayes import MultinomialNB
from sklearn.svm import LinearSVC
from sklearn.tree import DecisionTreeClassifier


OUT = Path(__file__).resolve().parent
DATA = ROOT / "data"
SEED = 42
BOOTSTRAPS = 100
POLICIES = {
    "all_keys_v1": "primary",
    "body_combined_only_v1": "body_combined_only",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical(payload: object) -> bytes:
    return json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def normalize_key(value: object) -> str:
    import unicodedata

    text = unicodedata.normalize("NFKC", "" if value is None else str(value)).casefold()
    return " ".join("".join(ch if ch.isalnum() else " " for ch in text).split()).strip()


def load_rows() -> dict[str, dict[str, object]]:
    rows = {}
    for path, label, prefix in [(DATA / "Fake.csv", 0, "fake"), (DATA / "True.csv", 1, "true")]:
        with path.open(encoding="utf-8-sig", newline="") as handle:
            for ordinal, record in enumerate(csv.DictReader(handle)):
                rows[f"{prefix}:{ordinal}"] = {
                    "row_id": f"{prefix}:{ordinal}",
                    "title": record.get("title") or "",
                    "body": record.get("text") or "",
                    "label": label,
                    "source_file": path.name,
                    "source_ordinal": ordinal,
                }
    return rows


def load_manifest(directory: Path, filename: str) -> list[dict[str, str]]:
    with (directory / filename).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def preflight(rows: dict[str, dict[str, object]], policy: str, directory: Path) -> dict[str, object]:
    outer = load_manifest(directory, "split_manifest.csv")
    inner = load_manifest(directory, "inner_split_manifest.csv")
    source_ids = set(rows)
    outer_ids = [r["row_id"] for r in outer]
    inner_ids = {r["row_id"] for r in inner}
    train_ids = {r["row_id"] for r in outer if r["partition"] == "train"}
    if set(outer_ids) != source_ids or len(outer_ids) != len(set(outer_ids)):
        raise RuntimeError(f"{policy}: outer manifest does not exactly cover source rows")
    if inner_ids != train_ids or inner_ids & {r["row_id"] for r in outer if r["partition"] == "test"}:
        raise RuntimeError(f"{policy}: inner manifest boundary mismatch")
    for item in outer:
        source = rows[item["row_id"]]
        if (item["source_file"], int(item["source_ordinal"]), int(item["label"])) != (source["source_file"], source["source_ordinal"], source["label"]):
            raise RuntimeError(f"{policy}: source metadata mismatch for {item['row_id']}")
    group_partitions = defaultdict(set)
    key_partitions = defaultdict(set)
    key_types = ("title", "body", "combined") if policy == "all_keys_v1" else ("body", "combined")
    for item in outer:
        group_partitions[item["group_id"]].add(item["partition"])
        source = rows[item["row_id"]]
        values = {
            "title": normalize_key(source["title"]),
            "body": normalize_key(source["body"]),
            "combined": normalize_key(f"{source['title']} {source['body']}"),
        }
        for key_type in key_types:
            if values[key_type]:
                key_partitions[(key_type, values[key_type])].add(item["partition"])
    if any(len(parts) != 1 for parts in group_partitions.values()):
        raise RuntimeError(f"{policy}: group crosses outer partitions")
    if any(len(parts) != 1 for parts in key_partitions.values()):
        raise RuntimeError(f"{policy}: normalized key crosses outer partitions")
    return {
        "policy": policy,
        "source_row_count": len(rows),
        "outer_rows": len(outer),
        "outer_partition_counts": dict(Counter(r["partition"] for r in outer)),
        "inner_rows": len(inner),
        "inner_partition_counts": dict(Counter(r["partition"] for r in inner)),
        "outer_group_count": len(group_partitions),
        "outer_groups_crossing_partitions": 0,
        "outer_keys_crossing_partitions": 0,
        "training_ids": sorted(train_ids),
        "method_selection_ids": sorted(r["row_id"] for r in inner if r["partition"] == "method_selection"),
        "final_calibration_ids": sorted(r["row_id"] for r in inner if r["partition"] == "final_calibration"),
        "outer_test_ids": sorted(r["row_id"] for r in outer if r["partition"] == "test"),
    }


def models() -> dict[str, object]:
    return {
        "lr": LogisticRegression(max_iter=1000, C=5.0, random_state=SEED),
        "dt": DecisionTreeClassifier(max_depth=None, random_state=SEED),
        "gbc": GradientBoostingClassifier(n_estimators=50, random_state=SEED),
        "nb": MultinomialNB(alpha=0.01),
        "svc": LinearSVC(C=1.0, max_iter=2000, random_state=SEED),
    }


def model_type(name: str) -> str:
    return {"lr": "Logistic Regression", "dt": "Decision Tree", "gbc": "Gradient Boosting", "nb": "Multinomial Naive Bayes", "svc": "Linear SVC"}[name]


def scores_and_probabilities(model, matrix):
    if hasattr(model, "predict_proba"):
        probability = np.asarray(model.predict_proba(matrix)[:, 1], dtype=float)
        prediction = (probability >= 0.5).astype(int)
        return prediction, probability, "predict_proba"
    decision = np.asarray(model.decision_function(matrix), dtype=float)
    probability = 1.0 / (1.0 + np.exp(-np.clip(decision, -60, 60)))
    return (decision >= 0).astype(int), probability, "sigmoid_of_decision_for_metrics"


def metric_dict(labels, predictions, probabilities) -> tuple[dict[str, object], list[dict[str, object]]]:
    labels = np.asarray(labels, dtype=int)
    predictions = np.asarray(predictions, dtype=int)
    probabilities = np.asarray(probabilities, dtype=float)
    finite = bool(np.isfinite(probabilities).all() and ((probabilities >= 0) & (probabilities <= 1)).all())
    if not finite:
        raise RuntimeError("non-finite or out-of-range probabilities")
    precision, recall, f1, support = precision_recall_fscore_support(labels, predictions, labels=[0, 1], zero_division=np.nan)
    cm = confusion_matrix(labels, predictions, labels=[0, 1]).tolist()
    bins = []
    for low, high in zip(np.linspace(0, 1, 11)[:-1], np.linspace(0, 1, 11)[1:]):
        mask = (probabilities >= low) & ((probabilities < high) if high < 1 else (probabilities <= high))
        if mask.any():
            bins.append({"lower": float(low), "upper": float(high), "count": int(mask.sum()), "mean_probability": float(probabilities[mask].mean()), "fraction_positive": float(labels[mask].mean())})
    ece = float(sum(item["count"] / len(labels) * abs(item["mean_probability"] - item["fraction_positive"]) for item in bins))
    result = {
        "n": int(len(labels)),
        "accuracy": float(accuracy_score(labels, predictions)),
        "precision_fake": float(precision[0]), "recall_fake": float(recall[0]), "f1_fake": float(f1[0]),
        "precision_real": float(precision[1]), "recall_real": float(recall[1]), "f1_real": float(f1[1]),
        "macro_f1": float(f1_score(labels, predictions, average="macro")),
        "balanced_accuracy": float(balanced_accuracy_score(labels, predictions)),
        "confusion_matrix_class_order_0_fake_1_real": cm,
        "roc_auc": float(roc_auc_score(labels, probabilities)),
        "pr_auc_positive_real": float(average_precision_score(labels, probabilities)),
        "log_loss": float(log_loss(labels, probabilities, labels=[0, 1])),
        "brier_score": float(brier_score_loss(labels, probabilities)),
        "ece_uniform_10_bins": ece,
        "probabilities_valid": finite,
        "support_fake": int(support[0]), "support_real": int(support[1]),
    }
    return result, bins


def group_bootstrap(labels, predictions, probabilities, groups, seed=SEED):
    rng = np.random.default_rng(seed)
    unique = np.array(sorted(set(groups)))
    by_group = {group: np.where(np.asarray(groups) == group)[0] for group in unique}
    values = defaultdict(list)
    for _ in range(BOOTSTRAPS):
        sampled = rng.choice(unique, size=len(unique), replace=True)
        indices = np.concatenate([by_group[group] for group in sampled])
        metrics, _ = metric_dict(np.asarray(labels)[indices], np.asarray(predictions)[indices], np.asarray(probabilities)[indices])
        for key in ("accuracy", "macro_f1", "balanced_accuracy", "roc_auc", "brier_score", "log_loss", "ece_uniform_10_bins"):
            values[key].append(metrics[key])
    return {key: {"lower_2.5_percent": float(np.percentile(vals, 2.5)), "upper_97.5_percent": float(np.percentile(vals, 97.5)), "replicates": BOOTSTRAPS, "resampling_unit": "outer-test connected component group", "seed": seed} for key, vals in values.items()}


def run_policy(policy: str, directory: Path, rows: dict[str, dict[str, object]]):
    outer = load_manifest(directory, "split_manifest.csv")
    inner = load_manifest(directory, "inner_split_manifest.csv")
    assignment = {r["row_id"]: r["partition"] for r in outer}
    inner_assignment = {r["row_id"]: r["partition"] for r in inner}
    texts = {row_id: preprocess(row["title"], row["body"]) for row_id, row in rows.items()}
    proper = [row_id for row_id, part in inner_assignment.items() if part == "proper_fit"]
    method = [row_id for row_id, part in inner_assignment.items() if part == "method_selection"]
    calibration = [row_id for row_id, part in inner_assignment.items() if part == "final_calibration"]
    test = [row_id for row_id, part in assignment.items() if part == "test"]
    vectorizer = TfidfVectorizer(ngram_range=(1, 2), max_features=150_000, sublinear_tf=True, analyzer="word", min_df=2, max_df=0.95)
    fit_text = [texts[row_id] for row_id in proper]
    fit_labels = np.array([rows[row_id]["label"] for row_id in proper])
    method_labels = np.array([rows[row_id]["label"] for row_id in method])
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        fit_matrix = vectorizer.fit_transform(fit_text)
    method_matrix = vectorizer.transform([texts[row_id] for row_id in method])
    calibration_matrix = vectorizer.transform([texts[row_id] for row_id in calibration])
    test_matrix = vectorizer.transform([texts[row_id] for row_id in test])
    candidates = []
    failures = []
    for key, estimator in models().items():
        started = time.time()
        try:
            representation = "tfidf_sparse"
            train_matrix, selection_matrix = fit_matrix, method_matrix
            if key == "gbc":
                components = min(256, max(2, fit_matrix.shape[1] - 1))
                reducer = TruncatedSVD(n_components=components, random_state=SEED)
                train_matrix = reducer.fit_transform(fit_matrix)
                selection_matrix = reducer.transform(method_matrix)
                representation = f"TruncatedSVD_{components}_fit_on_proper_fit"
            estimator.fit(train_matrix, fit_labels)
            predictions, probabilities, probability_source = scores_and_probabilities(estimator, selection_matrix)
            metrics, _ = metric_dict(method_labels, predictions, probabilities)
            candidates.append({"model_key": key, "model_name": model_type(key), "representation": representation, "probability_source": probability_source, "fit_seconds": time.time() - started, **metrics, "status": "success"})
        except Exception as exc:
            failures.append({"model_key": key, "model_name": model_type(key), "status": "fit_failed", "error": repr(exc), "fit_seconds": time.time() - started})
    if not candidates:
        raise RuntimeError(f"{policy}: no candidate model succeeded")
    selected = sorted(candidates, key=lambda item: (-item["macro_f1"], -item["balanced_accuracy"], item["model_key"]))[0]
    selected_key = selected["model_key"]
    selected_model = models()[selected_key]
    reducer = None
    selected_fit, selected_cal, selected_test = fit_matrix, calibration_matrix, test_matrix
    if selected_key == "gbc":
        components = min(256, max(2, fit_matrix.shape[1] - 1)); reducer = TruncatedSVD(n_components=components, random_state=SEED); selected_fit = reducer.fit_transform(fit_matrix); selected_cal = reducer.transform(calibration_matrix); selected_test = reducer.transform(test_matrix)
    selected_model.fit(selected_fit, fit_labels)
    _, cal_uncal_prob, uncal_source = scores_and_probabilities(selected_model, selected_cal)
    cal_score = np.asarray(selected_model.decision_function(selected_cal), dtype=float) if hasattr(selected_model, "decision_function") else np.log(np.clip(cal_uncal_prob, 1e-7, 1 - 1e-7) / np.clip(1 - cal_uncal_prob, 1e-7, 1))
    calibrator = LogisticRegression(C=1e6, max_iter=1000, random_state=SEED)
    calibrator.fit(cal_score.reshape(-1, 1), np.array([rows[row_id]["label"] for row_id in calibration]))
    test_predictions, test_uncal_prob, _ = scores_and_probabilities(selected_model, selected_test)
    test_score = np.asarray(selected_model.decision_function(selected_test), dtype=float) if hasattr(selected_model, "decision_function") else np.log(np.clip(test_uncal_prob, 1e-7, 1 - 1e-7) / np.clip(1 - test_uncal_prob, 1e-7, 1))
    calibrated_prob = calibrator.predict_proba(test_score.reshape(-1, 1))[:, list(calibrator.classes_).index(1)]
    calibrated_pred = (calibrated_prob >= 0.5).astype(int)
    test_labels = np.array([rows[row_id]["label"] for row_id in test])
    raw_metrics, raw_bins = metric_dict(test_labels, test_predictions, test_uncal_prob)
    calibrated_metrics, calibrated_bins = metric_dict(test_labels, calibrated_pred, calibrated_prob)
    outer_group_by_row = {item["row_id"]: item["group_id"] for item in outer}
    test_groups = [outer_group_by_row[row_id] for row_id in test]
    predictions = [{"policy": policy, "row_id": row_id, "group_id": group, "label": int(label), "uncalibrated_probability": float(raw), "calibrated_probability": float(cal), "uncalibrated_prediction": int(raw_pred), "calibrated_prediction": int(cal_pred)} for row_id, group, label, raw, cal, raw_pred, cal_pred in zip(test, test_groups, test_labels, test_uncal_prob, calibrated_prob, test_predictions, calibrated_pred)]
    return {"selection": {"rule": "highest method-selection macro-F1; tie balanced accuracy then model key", "selected_model": selected, "candidates": candidates, "failures": failures, "warnings": [str(w.message) for w in caught]}, "selected_key": selected_key, "outer": {"uncalibrated": raw_metrics, "calibrated": calibrated_metrics, "uncalibrated_bins": raw_bins, "calibrated_bins": calibrated_bins}, "predictions": predictions, "uncertainty": {"uncalibrated": group_bootstrap(test_labels, test_predictions, test_uncal_prob, test_groups), "calibrated": group_bootstrap(test_labels, calibrated_pred, calibrated_prob, test_groups)}, "fit_counts": {"proper_fit": len(proper), "method_selection": len(method), "final_calibration": len(calibration), "outer_test": len(test)}, "vocabulary_size": len(vectorizer.vocabulary_), "selected_probability_source": uncal_source, "calibration": {"method": "sigmoid", "fit_partition": "final_calibration", "positive_class": 1, "calibrator_classes": calibrator.classes_.tolist()}}


def main():
    rows = load_rows()
    source_provenance = {}
    for name, label in [("Fake.csv", 0), ("True.csv", 1)]:
        source_path = DATA / name
        frame = pd.read_csv(source_path)
        columns = list(frame.columns)
        source_provenance[name] = {
            "relative_path": f"data/{name}",
            "sha256": sha256(source_path),
            "size_bytes": source_path.stat().st_size,
            "row_count": int(len(frame)),
            "ordered_columns": columns,
            "schema_fingerprint": hashlib.sha256(canonical({"columns": columns})).hexdigest(),
            "label": label,
            "source_to_label_rule": f"all rows from {name} map to class {label}",
        }
    validation = {}
    results = {}
    all_predictions = []
    curves = []
    for policy, directory_name in POLICIES.items():
        directory = ROOT / "evaluation_results" / "duplicate_aware" / "final_v5" / directory_name
        validation[policy] = preflight(rows, policy, directory)
        results[policy] = run_policy(policy, directory, rows)
        all_predictions.extend(results[policy].pop("predictions"))
        for stage in ("uncalibrated", "calibrated"):
            for item in results[policy]["outer"][stage + "_bins"]:
                curves.append({"policy": policy, "stage": stage, **item})
        results[policy]["outer"].pop("uncalibrated_bins")
        results[policy]["outer"].pop("calibrated_bins")
    (OUT / "source_provenance.json").write_text(json.dumps(source_provenance, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (OUT / "preflight_validation.json").write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (OUT / "outer_test_metrics.json").write_text(json.dumps({p: r["outer"] for p, r in results.items()}, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")
    (OUT / "calibration_metrics.json").write_text(json.dumps({p: r["calibration"] for p, r in results.items()}, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (OUT / "uncertainty_intervals.json").write_text(json.dumps({p: r["uncertainty"] for p, r in results.items()}, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    confusion_payload = {"axis_order": ["Fake", "Real"], "class_order": [0, 1], "policies": {p: {s: r["outer"][s]["confusion_matrix_class_order_0_fake_1_real"] for s in ("uncalibrated", "calibrated")} for p, r in results.items()}}
    (OUT / "confusion_matrices.json").write_text(json.dumps(confusion_payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    pd.DataFrame([c for p, r in results.items() for c in r["selection"]["candidates"]] + [f for p, r in results.items() for f in r["selection"]["failures"]]).to_csv(OUT / "method_selection_metrics.csv", index=False)
    pd.DataFrame(curves).to_csv(OUT / "calibration_curve_data.csv", index=False)
    pd.DataFrame(all_predictions).to_csv(OUT / "outer_predictions.csv", index=False)
    environment = {"python": sys.version, "platform": platform.platform(), "executable": sys.executable, "sklearn": sklearn.__version__, "numpy": np.__version__, "pandas": pd.__version__, "spacy": spacy.__version__, "en_core_web_sm": spacy.util.get_package_path("en_core_web_sm").as_posix(), "seed": SEED}
    (OUT / "environment_versions.json").write_text(json.dumps(environment, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    selection_summary = {p: {"selected_model": r["selected_key"], "fit_counts": r["fit_counts"], "vocabulary_size": r["vocabulary_size"], "failures": r["selection"]["failures"]} for p, r in results.items()}
    (OUT / "selection_summary.json").write_text(json.dumps(selection_summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    with (OUT / "run_log.txt").open("w", encoding="utf-8") as log:
        log.write("Fresh group-aware evaluation completed.\n")
        log.write("Production spaCy preprocessing used via preprocessor.preprocess; no fallback.\n")
        log.write(json.dumps(selection_summary, sort_keys=True) + "\n")
    files = [p for p in OUT.rglob("*") if p.is_file() and p.name != "artifact_hashes.json"]
    hashes = {p.relative_to(OUT).as_posix(): sha256(p) for p in sorted(files)}
    (OUT / "artifact_hashes.json").write_text(json.dumps(hashes, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
