"""Standalone rigorous evaluation for the fake-news detection pipeline.

This script intentionally does not modify or call the production training and
inference code paths. It reuses only the existing ``preprocess`` function and
fits fresh evaluators for every CV fold and for the final held-out evaluation.
"""

import difflib
import json
import os
from collections import Counter
from typing import Dict, Iterable, Tuple

import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    precision_recall_fscore_support,
)
from sklearn.model_selection import StratifiedKFold, train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn.svm import LinearSVC
from sklearn.tree import DecisionTreeClassifier

from preprocessor import preprocess


RANDOM_STATE = 42
HELD_OUT_FRACTION = 0.15
CV_FOLDS = 5
NEAR_DUPLICATE_THRESHOLD = 0.90
NEAR_DUPLICATE_SAMPLE_SIZE = 500
NEAR_DUPLICATE_WINDOW = 5
NEAR_DUPLICATE_MAX_CHARS = 2000
RESULTS_DIR = "evaluation_results"
HELD_OUT_PATH = os.path.join(RESULTS_DIR, "held_out_test_set.csv")
REPORT_PATH = os.path.join(RESULTS_DIR, "phase1_evaluation_report.json")

MODEL_NAMES = {
    "lr": "Logistic Regression",
    "dt": "Decision Tree",
    "gbc": "Gradient Boosting",
    "rfc": "Random Forest",
    "nb": "Naive Bayes",
    "svc": "Linear SVC",
}


def build_models() -> Dict[str, object]:
    """Create fresh models with the hyperparameters from train.py."""
    return {
        "lr": LogisticRegression(max_iter=1000, C=5.0, random_state=RANDOM_STATE),
        "dt": DecisionTreeClassifier(max_depth=None, random_state=RANDOM_STATE),
        "gbc": GradientBoostingClassifier(n_estimators=200, random_state=RANDOM_STATE),
        "rfc": RandomForestClassifier(
            n_estimators=200, random_state=RANDOM_STATE, n_jobs=-1
        ),
        "nb": MultinomialNB(alpha=0.01),
        "svc": LinearSVC(C=1.0, max_iter=2000, random_state=RANDOM_STATE),
    }


def load_dataset() -> pd.DataFrame:
    """Load the two project CSVs using train.py's columns and labels."""
    fake = pd.read_csv(os.path.join("data", "Fake.csv"))
    true = pd.read_csv(os.path.join("data", "True.csv"))

    fake["class"] = 0
    true["class"] = 1
    data = pd.concat([fake, true], ignore_index=True)
    data["title"] = data["title"].fillna("")
    data["text"] = data["text"].fillna("")
    data["combined_text"] = data["title"] + " " + data["text"]
    return data


def duplicate_key(value: str) -> str:
    return " ".join(str(value).lower().split())


def exact_cross_class_duplicates(data: pd.DataFrame) -> Dict[str, object]:
    """Find exact normalized title+text duplicates occurring in both classes."""
    normalized = data["combined_text"].map(duplicate_key)
    fake_keys = set(normalized[data["class"] == 0])
    true_keys = set(normalized[data["class"] == 1])
    overlap = sorted(fake_keys & true_keys)
    return {
        "fake_unique_texts": len(fake_keys),
        "true_unique_texts": len(true_keys),
        "cross_class_duplicate_text_count": len(overlap),
        "cross_class_duplicate_examples": overlap[:10],
        "flagged": bool(overlap),
    }


def sample_near_duplicates(
    data: pd.DataFrame,
    sample_size: int = NEAR_DUPLICATE_SAMPLE_SIZE,
    window: int = NEAR_DUPLICATE_WINDOW,
    threshold: float = NEAR_DUPLICATE_THRESHOLD,
) -> Dict[str, object]:
    """Sample each class and compare nearby lengths instead of all pairs."""
    results = {}
    rng = np.random.RandomState(RANDOM_STATE)

    for class_value, class_name in ((0, "fake"), (1, "true")):
        class_data = data[data["class"] == class_value]
        sample_count = min(sample_size, len(class_data))
        sample = class_data.sample(n=sample_count, random_state=rng).copy()
        sample["normalized"] = sample["combined_text"].map(duplicate_key)
        sample["length"] = sample["normalized"].str.len()
        sample["comparison_text"] = sample["normalized"].str[:NEAR_DUPLICATE_MAX_CHARS]
        sample = sample.sort_values("length").reset_index(drop=True)

        compared_pairs = 0
        flagged_pairs = []
        flagged_articles = set()
        for index, row in sample.iterrows():
            for neighbor_index in range(index + 1, min(index + 1 + window, len(sample))):
                neighbor = sample.iloc[neighbor_index]
                compared_pairs += 1
                if not row["comparison_text"] or not neighbor["comparison_text"]:
                    continue
                matcher = difflib.SequenceMatcher(
                    None, row["comparison_text"], neighbor["comparison_text"]
                )
                if matcher.quick_ratio() < threshold:
                    continue
                ratio = matcher.ratio()
                if ratio >= threshold:
                    flagged_pairs.append(
                        {
                            "sample_index_a": int(row.name),
                            "sample_index_b": int(neighbor.name),
                            "similarity": round(ratio, 4),
                        }
                    )
                    flagged_articles.update((int(row.name), int(neighbor.name)))

        rate = len(flagged_articles) / sample_count if sample_count else 0.0
        results[class_name] = {
            "sample_size": sample_count,
            "comparison_window": window,
            "compared_pairs": compared_pairs,
            "threshold": threshold,
            "near_duplicate_pairs": len(flagged_pairs),
            "near_duplicate_articles": len(flagged_articles),
            "near_duplicate_rate": round(rate, 6),
            "flagged_over_5_percent": rate > 0.05,
            "examples": flagged_pairs[:10],
        }

    results["method"] = (
        "Each class was sampled with a fixed seed, sorted by normalized text length, "
        f"and compared using the first {NEAR_DUPLICATE_MAX_CHARS} normalized characters "
        "against the next local length window; this is not a full pairwise scan."
    )
    return results


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


def metric_record(y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, object]:
    precision, recall, f1, _ = precision_recall_fscore_support(
        y_true, y_pred, average="weighted", zero_division=0
    )
    return {
        "accuracy": round(float(accuracy_score(y_true, y_pred)), 6),
        "precision_weighted": round(float(precision), 6),
        "recall_weighted": round(float(recall), 6),
        "f1_weighted": round(float(f1), 6),
        "confusion_matrix": confusion_matrix(y_true, y_pred, labels=[0, 1]).tolist(),
    }


def run_cross_validation(texts: pd.Series, labels: pd.Series) -> Dict[str, object]:
    print("\n[4/6] Running 5-fold stratified cross-validation...")
    splitter = StratifiedKFold(n_splits=CV_FOLDS, shuffle=True, random_state=RANDOM_STATE)
    fold_scores = {key: [] for key in MODEL_NAMES}

    for fold, (train_indices, validation_indices) in enumerate(
        splitter.split(texts, labels), start=1
    ):
        print(f"  Fold {fold}/{CV_FOLDS}: fitting fold-specific TF-IDF...")
        fold_train = texts.iloc[train_indices]
        fold_validation = texts.iloc[validation_indices]
        _, train_vectors, validation_vectors = vectorize(fold_train, fold_validation)
        fold_models = build_models()
        for key, model in fold_models.items():
            model.fit(train_vectors, labels.iloc[train_indices])
            predictions = model.predict(validation_vectors)
            score = float(accuracy_score(labels.iloc[validation_indices], predictions))
            fold_scores[key].append(round(score, 6))
            print(f"    {MODEL_NAMES[key]}: {score:.4f}")

    summary = {}
    for key, scores in fold_scores.items():
        mean = float(np.mean(scores))
        std = float(np.std(scores, ddof=1))
        summary[key] = {
            "name": MODEL_NAMES[key],
            "fold_accuracy": scores,
            "mean_accuracy": round(mean, 6),
            "std_accuracy": round(std, 6),
            "potentially_unstable": std > 0.02,
        }
    return summary


def majority_vote(predictions: Dict[str, np.ndarray]) -> Tuple[np.ndarray, int]:
    matrix = np.vstack([predictions[key] for key in MODEL_NAMES])
    real_votes = matrix.sum(axis=0)
    ties = int(np.sum(real_votes == len(MODEL_NAMES) / 2))
    # Six models can tie. Use class 1 (true) as the documented deterministic tie-break.
    return (real_votes >= (len(MODEL_NAMES) / 2)).astype(int), ties


def evaluate_final(
    train_texts: pd.Series,
    train_labels: pd.Series,
    held_out_texts: pd.Series,
    held_out_labels: pd.Series,
) -> Dict[str, object]:
    print("\n[5/6] Fitting on all non-held-out data and evaluating once...")
    _, train_vectors, held_out_vectors = vectorize(train_texts, held_out_texts)
    predictions = {}
    metrics = {}

    for key, model in build_models().items():
        print(f"  Fitting {MODEL_NAMES[key]}...")
        model.fit(train_vectors, train_labels)
        predictions[key] = model.predict(held_out_vectors)
        metrics[key] = {
            "name": MODEL_NAMES[key],
            **metric_record(held_out_labels, predictions[key]),
        }
        print(classification_report(held_out_labels, predictions[key], labels=[0, 1], zero_division=0))

    ensemble_predictions, tie_count = majority_vote(predictions)
    ensemble_metrics = metric_record(held_out_labels, ensemble_predictions)
    ensemble_metrics.update(
        {
            "name": "Six-model majority-vote ensemble",
            "tie_count": tie_count,
            "tie_break": "class 1 (true) when three fake and three true votes occur",
        }
    )
    print("  Six-model majority-vote ensemble:")
    print(classification_report(held_out_labels, ensemble_predictions, labels=[0, 1], zero_division=0))
    metrics["ensemble"] = ensemble_metrics
    return metrics


def main() -> None:
    print("[1/6] Loading data and applying the existing preprocessing function...")
    data = load_dataset()
    print(f"  Total rows: {len(data):,}")
    print(f"  Class distribution: {dict(sorted(Counter(data['class']).items()))} (0=fake, 1=true)")
    data["processed"] = [
        preprocess(row.title, row.text) for row in data.itertuples(index=False)
    ]
    print("  Preprocessing complete.")

    print("\n[2/6] Checking exact cross-class duplicates and sampled near-duplicates...")
    duplicate_results = exact_cross_class_duplicates(data)
    near_duplicate_results = sample_near_duplicates(data)
    print(
        "  Exact cross-class duplicate texts: "
        f"{duplicate_results['cross_class_duplicate_text_count']}"
    )
    for class_name in ("fake", "true"):
        result = near_duplicate_results[class_name]
        print(
            f"  {class_name.title()} near-duplicate sample rate: "
            f"{result['near_duplicate_rate']:.2%} "
            f"({'FLAGGED' if result['flagged_over_5_percent'] else 'below 5% threshold'})"
        )

    print("\n[3/6] Creating the untouched stratified held-out test set...")
    train_indices, held_out_indices = train_test_split(
        np.arange(len(data)),
        test_size=HELD_OUT_FRACTION,
        random_state=RANDOM_STATE,
        stratify=data["class"],
    )
    held_out = data.iloc[held_out_indices][["title", "text", "class"]].copy()
    os.makedirs(RESULTS_DIR, exist_ok=True)
    held_out.to_csv(HELD_OUT_PATH, index=False)
    print(f"  Saved {len(held_out):,} rows to {HELD_OUT_PATH}")
    print(f"  Remaining training/evaluation rows: {len(train_indices):,}")

    train_texts = data.iloc[train_indices]["processed"].reset_index(drop=True)
    train_labels = data.iloc[train_indices]["class"].reset_index(drop=True)
    held_out_texts = data.iloc[held_out_indices]["processed"].reset_index(drop=True)
    held_out_labels = data.iloc[held_out_indices]["class"].reset_index(drop=True)

    cv_summary = run_cross_validation(train_texts, train_labels)
    final_metrics = evaluate_final(
        train_texts, train_labels, held_out_texts, held_out_labels
    )

    report = {
        "configuration": {
            "random_state": RANDOM_STATE,
            "held_out_fraction": HELD_OUT_FRACTION,
            "cv_folds": CV_FOLDS,
            "tfidf": {
                "ngram_range": [1, 2],
                "max_features": 150000,
                "sublinear_tf": True,
                "analyzer": "word",
                "min_df": 2,
                "max_df": 0.95,
            },
            "models": list(MODEL_NAMES.values()),
        },
        "data": {
            "total_rows": len(data),
            "class_distribution": {
                "fake_0": int((data["class"] == 0).sum()),
                "true_1": int((data["class"] == 1).sum()),
            },
            "held_out_rows": len(held_out),
            "training_rows_for_cv_and_final_fit": len(train_indices),
            "held_out_file": HELD_OUT_PATH,
        },
        "duplicate_checks": {
            "exact_cross_class": duplicate_results,
            "sampled_near_duplicates": near_duplicate_results,
        },
        "cross_validation": cv_summary,
        "final_held_out_evaluation": final_metrics,
    }
    with open(REPORT_PATH, "w", encoding="utf-8") as report_file:
        json.dump(report, report_file, indent=2)
    print(f"\n[6/6] Wrote complete JSON report to {REPORT_PATH}")
    print(
        "  Ensemble held-out accuracy: "
        f"{final_metrics['ensemble']['accuracy']:.4f}"
    )


if __name__ == "__main__":
    main()