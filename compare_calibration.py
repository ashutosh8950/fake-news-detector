"""Compare existing uncalibrated artifacts with Phase 2 calibrated artifacts."""

import json
import os
import sys

import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, brier_score_loss

from preprocessor import preprocess


MODEL_KEYS = ["lr", "dt", "gbc", "rfc", "nb", "svc"]
MODEL_NAMES = {
    "lr": "Logistic Regression",
    "dt": "Decision Tree",
    "gbc": "Gradient Boosting",
    "rfc": "Random Forest",
    "nb": "Naive Bayes",
    "svc": "Linear SVC",
}
MODEL_DIR = "models"
CALIBRATED_DIR = os.path.join(MODEL_DIR, "calibrated")
HELD_OUT_PATH = os.path.join("evaluation_results", "held_out_test_set.csv")
REPORT_PATH = os.path.join("evaluation_results", "phase2_calibration_report.json")
COMPARISON_PATH = os.path.join("evaluation_results", "phase2_comparison.json")


def old_class_one_probability(model, vectors):
    if hasattr(model, "predict_proba"):
        return model.predict_proba(vectors)[:, 1]
    scores = model.decision_function(vectors)
    return 1.0 / (1.0 + np.exp(-np.clip(scores, -60, 60)))


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if not os.path.exists(REPORT_PATH):
        raise FileNotFoundError("Run phase2_calibration.py before this comparison.")

    held_out = pd.read_csv(HELD_OUT_PATH).fillna("")
    processed = [preprocess(row.title, row.text) for row in held_out.itertuples(index=False)]

    old_vectorizer = joblib.load(os.path.join(MODEL_DIR, "vectorizer.pkl"))
    new_vectorizer = joblib.load(os.path.join(CALIBRATED_DIR, "vectorizer.pkl"))
    old_vectors = old_vectorizer.transform(processed)
    new_vectors = new_vectorizer.transform(processed)
    labels = held_out["class"].to_numpy()

    with open(os.path.join(MODEL_DIR, "model_meta.json"), encoding="utf-8") as metadata_file:
        metadata = json.load(metadata_file)

    old_predictions = {}
    new_probabilities = {}
    rows = []
    for key in MODEL_KEYS:
        old_model = joblib.load(os.path.join(MODEL_DIR, f"{key}_model.pkl"))
        new_model = joblib.load(os.path.join(CALIBRATED_DIR, f"{key}_calibrated.pkl"))
        old_pred = old_model.predict(old_vectors).astype(int)
        old_probability_class1 = old_class_one_probability(old_model, old_vectors)
        new_probability = new_model.predict_proba(new_vectors)[:, 1]
        new_pred = (new_probability >= 0.5).astype(int)
        old_confidence = np.where(old_pred == 1, old_probability_class1, 1.0 - old_probability_class1)
        new_confidence = np.where(new_pred == 1, new_probability, 1.0 - new_probability)
        old_predictions[key] = old_pred
        new_probabilities[key] = new_probability
        rows.append(
            {
                "key": key,
                "model": MODEL_NAMES[key],
                "old_accuracy": round(float(accuracy_score(labels, old_pred)), 6),
                "new_accuracy": round(float(accuracy_score(labels, new_pred)), 6),
                "old_brier_score": round(
                    float(brier_score_loss(labels, old_probability_class1)), 6
                ),
                "new_brier_score": round(float(brier_score_loss(labels, new_probability)), 6),
                "old_artifact_accuracy_metadata": metadata.get(key, {}).get("accuracy"),
            }
        )

    old_matrix = np.vstack([old_predictions[key] for key in MODEL_KEYS])
    old_real_votes = old_matrix.sum(axis=0)
    old_ensemble_pred = (old_real_votes >= 3).astype(int)
    old_ensemble_confidence = np.where(
        old_ensemble_pred == 1,
        old_real_votes / 6.0,
        1.0 - old_real_votes / 6.0,
    )
    old_ensemble_probability = old_real_votes / 6.0
    new_matrix = np.vstack([new_probabilities[key] for key in MODEL_KEYS])
    new_ensemble_probability = new_matrix.mean(axis=0)
    new_ensemble_pred = (new_ensemble_probability >= 0.5).astype(int)
    new_ensemble_confidence = np.where(
        new_ensemble_pred == 1,
        new_ensemble_probability,
        1.0 - new_ensemble_probability,
    )
    rows.append(
        {
            "key": "ensemble",
            "model": "Six-model ensemble",
            "old_accuracy": round(float(accuracy_score(labels, old_ensemble_pred)), 6),
            "new_accuracy": round(float(accuracy_score(labels, new_ensemble_pred)), 6),
            "old_brier_score": round(
                float(brier_score_loss(labels, old_ensemble_probability)), 6
            ),
            "new_brier_score": round(
                float(brier_score_loss(labels, new_ensemble_probability)), 6
            ),
            "old_artifact_accuracy_metadata": "vote-share confidence, not probability",
        }
    )

    sample_indices = np.linspace(0, len(held_out) - 1, 10, dtype=int)
    samples = []
    for index in sample_indices:
        samples.append(
            {
                "held_out_row": int(index),
                "title": held_out.iloc[index]["title"],
                "true_label": "REAL" if labels[index] else "FAKE",
                "old_ensemble_confidence_percent": round(float(old_ensemble_confidence[index] * 100), 2),
                "new_ensemble_confidence_percent": round(float(new_ensemble_confidence[index] * 100), 2),
                "old_label": "REAL" if old_ensemble_pred[index] else "FAKE",
                "new_label": "REAL" if new_ensemble_pred[index] else "FAKE",
                "old_correct": bool(old_ensemble_pred[index] == labels[index]),
                "new_correct": bool(new_ensemble_pred[index] == labels[index]),
            }
        )

    comparison = {"metrics": rows, "sample_predictions": samples}
    with open(COMPARISON_PATH, "w", encoding="utf-8") as comparison_file:
        json.dump(comparison, comparison_file, indent=2)

    print("Model                         Old Acc   New Acc   Old Brier  New Brier")
    print("-" * 74)
    for row in rows:
        print(
            f"{row['model']:<29} {row['old_accuracy']:.4f}    "
            f"{row['new_accuracy']:.4f}    {row['old_brier_score']:.4f}     "
            f"{row['new_brier_score']:.4f}"
        )
    print("\nSample predictions (same held-out rows):")
    for sample in samples:
        print(
            f"row={sample['held_out_row']:4d} | true={sample['true_label']:<4} | "
            f"old={sample['old_label']:<4} ({'correct' if sample['old_correct'] else 'wrong':7}) "
            f"{sample['old_ensemble_confidence_percent']:6.2f}% | "
            f"new={sample['new_label']:<4} ({'correct' if sample['new_correct'] else 'wrong':7}) "
            f"{sample['new_ensemble_confidence_percent']:6.2f}% | "
            f"{sample['title'][:80]}"
        )
    print(f"\nSaved comparison JSON to {COMPARISON_PATH}")


if __name__ == "__main__":
    main()
