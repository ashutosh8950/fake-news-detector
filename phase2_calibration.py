"""Phase 2 calibration on the immutable Phase 1 held-out split.

This script does not modify production inference code or Phase 1 outputs. It
fits fresh models on the non-held-out rows, chooses sigmoid or isotonic
calibration using an inner training-only validation split, and saves calibrated
artifacts under models/calibrated/.
"""

import json
import os
from typing import Dict, Iterable

import joblib
import numpy as np
import pandas as pd
from sklearn.calibration import CalibratedClassifierCV, calibration_curve
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, brier_score_loss
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn.svm import LinearSVC
from sklearn.tree import DecisionTreeClassifier

from preprocessor import preprocess


RANDOM_STATE = 42
CALIBRATION_VALIDATION_FRACTION = 0.20
CALIBRATION_CV_FOLDS = 5
CALIBRATION_METHODS = ("sigmoid", "isotonic")
DATA_DIR = "data"
RESULTS_DIR = "evaluation_results"
HELD_OUT_PATH = os.path.join(RESULTS_DIR, "held_out_test_set.csv")
PHASE1_REPORT_PATH = os.path.join(RESULTS_DIR, "phase1_evaluation_report.json")
REPORT_PATH = os.path.join(RESULTS_DIR, "phase2_calibration_report.json")
CALIBRATED_DIR = os.path.join("models", "calibrated")

MODEL_NAMES = {
    "lr": "Logistic Regression",
    "dt": "Decision Tree",
    "gbc": "Gradient Boosting",
    "rfc": "Random Forest",
    "nb": "Naive Bayes",
    "svc": "Linear SVC",
}


def build_models() -> Dict[str, object]:
    return {
        "lr": LogisticRegression(max_iter=1000, C=5.0, random_state=RANDOM_STATE),
        "dt": DecisionTreeClassifier(max_depth=None, random_state=RANDOM_STATE),
        "gbc": GradientBoostingClassifier(n_estimators=200, random_state=RANDOM_STATE),
        "rfc": RandomForestClassifier(
            n_estimators=200, random_state=RANDOM_STATE, n_jobs=1
        ),
        "nb": MultinomialNB(alpha=0.01),
        "svc": LinearSVC(C=1.0, max_iter=2000, random_state=RANDOM_STATE),
    }


def vectorize(train_text: Iterable[str], test_text: Iterable[str] = None):
    vectorizer = TfidfVectorizer(
        ngram_range=(1, 2),
        max_features=150_000,
        sublinear_tf=True,
        analyzer="word",
        min_df=2,
        max_df=0.95,
    )
    train_vectors = vectorizer.fit_transform(train_text)
    test_vectors = vectorizer.transform(test_text) if test_text is not None else None
    return vectorizer, train_vectors, test_vectors


def load_phase1_data():
    if not os.path.exists(HELD_OUT_PATH) or not os.path.exists(PHASE1_REPORT_PATH):
        raise FileNotFoundError(
            "Phase 1 outputs are required: evaluation_results/held_out_test_set.csv "
            "and phase1_evaluation_report.json"
        )

    fake = pd.read_csv(os.path.join(DATA_DIR, "Fake.csv"))
    true = pd.read_csv(os.path.join(DATA_DIR, "True.csv"))
    fake["class"] = 0
    true["class"] = 1
    all_data = pd.concat([fake, true], ignore_index=True)
    all_data["title"] = all_data["title"].fillna("")
    all_data["text"] = all_data["text"].fillna("")

    held_out = pd.read_csv(HELD_OUT_PATH).fillna("")
    held_out_keys = set(zip(held_out["title"], held_out["text"], held_out["class"]))
    is_held_out = [
        (title, text, label) in held_out_keys
        for title, text, label in zip(
            all_data["title"], all_data["text"], all_data["class"]
        )
    ]
    train_data = all_data.loc[~np.array(is_held_out)].reset_index(drop=True)
    if len(train_data) != 20700 or len(held_out) != 3653:
        raise ValueError(
            f"Phase 1 split mismatch: expected 20,700/3,653 rows, got "
            f"{len(train_data)}/{len(held_out)}"
        )
    return train_data, held_out


def choose_calibration_method(
    estimator, train_vectors, labels: pd.Series
) -> Dict[str, object]:
    inner_train, inner_validation, y_inner_train, y_inner_validation = train_test_split(
        train_vectors,
        labels,
        test_size=CALIBRATION_VALIDATION_FRACTION,
        random_state=RANDOM_STATE,
        stratify=labels,
    )
    scores = {}
    for method in CALIBRATION_METHODS:
        print(f"    trying {method} calibration...")
        candidate = CalibratedClassifierCV(
            estimator=estimator,
            method=method,
            cv=CALIBRATION_CV_FOLDS,
            n_jobs=1,
        )
        candidate.fit(inner_train, y_inner_train)
        probabilities = candidate.predict_proba(inner_validation)[:, 1]
        scores[method] = {
            "brier_score": round(
                float(brier_score_loss(y_inner_validation, probabilities)), 6
            ),
            "accuracy": round(
                float(
                    accuracy_score(
                        y_inner_validation, (probabilities >= 0.5).astype(int)
                    )
                ),
                6,
            ),
        }

    selected = min(CALIBRATION_METHODS, key=lambda method: scores[method]["brier_score"])
    return {
        "selected_method": selected,
        "selection_metric": "lower inner training-only validation Brier score",
        "inner_validation_fraction": CALIBRATION_VALIDATION_FRACTION,
        "inner_cv_folds": CALIBRATION_CV_FOLDS,
        "method_scores": scores,
    }


def metrics_for_model(labels, predictions, probabilities) -> Dict[str, object]:
    curve_true, curve_predicted = calibration_curve(
        labels, probabilities, n_bins=10, strategy="uniform"
    )
    return {
        "accuracy": round(float(accuracy_score(labels, predictions)), 6),
        "brier_score": round(float(brier_score_loss(labels, probabilities)), 6),
        "reliability_curve": {
            "mean_predicted_probability": [round(float(value), 6) for value in curve_predicted],
            "fraction_of_positives": [round(float(value), 6) for value in curve_true],
            "n_bins": len(curve_true),
        },
    }


def main() -> None:
    print("[1/4] Loading the immutable Phase 1 split...")
    train_data, held_out = load_phase1_data()

    print(f"    preprocessing {len(train_data)} training rows...")
    processed_train = []
    for i, row in enumerate(train_data.itertuples(index=False)):
        processed_train.append(preprocess(row.title, row.text))
        if (i + 1) % 2000 == 0:
            print(f"    preprocessed {i + 1}/{len(train_data)} training rows...")
    train_data["processed"] = processed_train
    print(f"    preprocessed {len(train_data)}/{len(train_data)} training rows.")

    print(f"    preprocessing {len(held_out)} held-out rows...")
    processed_held_out = []
    for i, row in enumerate(held_out.itertuples(index=False)):
        processed_held_out.append(preprocess(row.title, row.text))
        if (i + 1) % 2000 == 0:
            print(f"    preprocessed {i + 1}/{len(held_out)} held-out rows...")
    held_out["processed"] = processed_held_out
    print(f"    preprocessed {len(held_out)}/{len(held_out)} held-out rows.")

    train_labels = train_data["class"].reset_index(drop=True)
    held_out_labels = held_out["class"].reset_index(drop=True)

    print("[2/4] Fitting fresh TF-IDF and selecting calibration methods...")
    vectorizer, train_vectors, held_out_vectors = vectorize(
        train_data["processed"], held_out["processed"]
    )
    os.makedirs(CALIBRATED_DIR, exist_ok=True)
    joblib.dump(vectorizer, os.path.join(CALIBRATED_DIR, "vectorizer.pkl"))

    report = {
        "phase": 2,
        "method": "CalibratedClassifierCV selected by inner training-only Brier score",
        "held_out_source": HELD_OUT_PATH,
        "held_out_rows": len(held_out),
        "training_rows": len(train_data),
        "random_state": RANDOM_STATE,
        "production_switch": False,
        "models": {},
    }
    calibrated_predictions = {}

    for key, base_model in build_models().items():
        print(f"  {MODEL_NAMES[key]}: comparing sigmoid and isotonic...")
        selection = choose_calibration_method(base_model, train_vectors, train_labels)
        selected = selection["selected_method"]
        print(f"    selected {selected}; fitting final calibrated model...")
        calibrated = CalibratedClassifierCV(
            estimator=base_model,
            method=selected,
            cv=CALIBRATION_CV_FOLDS,
            n_jobs=1,
        )
        calibrated.fit(train_vectors, train_labels)
        model_path = os.path.join(CALIBRATED_DIR, f"{key}_calibrated.pkl")
        joblib.dump(calibrated, model_path)

        probabilities = calibrated.predict_proba(held_out_vectors)[:, 1]
        predictions = (probabilities >= 0.5).astype(int)
        calibrated_predictions[key] = probabilities
        report["models"][key] = {
            "name": MODEL_NAMES[key],
            "artifact": model_path,
            "calibration_selection": selection,
            "held_out": metrics_for_model(
                held_out_labels, predictions, probabilities
            ),
        }
        print(
            f"    selected={selected}; accuracy="
            f"{report['models'][key]['held_out']['accuracy']:.4f}; "
            f"Brier={report['models'][key]['held_out']['brier_score']:.4f}"
        )

    print("[3/4] Measuring the calibrated majority-probability ensemble...")
    probability_matrix = np.vstack([calibrated_predictions[key] for key in MODEL_NAMES])
    ensemble_probabilities = probability_matrix.mean(axis=0)
    ensemble_predictions = (ensemble_probabilities >= 0.5).astype(int)
    report["ensemble"] = {
        "name": "Six-model average calibrated probability ensemble",
        "held_out": metrics_for_model(
            held_out_labels, ensemble_predictions, ensemble_probabilities
        ),
        "confidence_definition": (
            "Average of six calibrated P(class=1) values; confidence for the "
            "predicted class is ensemble probability when real, otherwise 1 minus it."
        ),
    }
    print(
        f"  accuracy={report['ensemble']['held_out']['accuracy']:.4f}; "
        f"Brier={report['ensemble']['held_out']['brier_score']:.4f}"
    )

    with open(REPORT_PATH, "w", encoding="utf-8") as report_file:
        json.dump(report, report_file, indent=2)
    print(f"[4/4] Wrote {REPORT_PATH}")


if __name__ == "__main__":
    main()