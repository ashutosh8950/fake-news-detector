"""
Ensemble prediction engine for Fake News Detection.
Loads the 5 production Phase 2 calibrated models and produces:
  - Per-model predictions + calibrated probabilities
  - Average-probability ensemble using calibrated P(class=1) values
  - Overall confidence = calibrated probability of the predicted class, as a percentage
"""

import json
import os
from datetime import datetime
from typing import Any, Dict

import joblib
import numpy as np
from loguru import logger

from artifact_contract import (
    extract_real_probability,
    validate_loaded_bundle,
    verify_artifact_bundle,
)
from config import settings
from preprocessor import preprocess

MODELS_DIR = os.path.join(settings.models_dir, "calibrated")
PHASE2_REPORT_PATH = os.path.join("evaluation_results", "phase2_calibration_report.json")

MODEL_KEYS = ["lr", "dt", "gbc", "nb", "svc"]
MODEL_NAMES = {
    "lr":  "Logistic Regression",
    "dt":  "Decision Tree",
    "gbc": "Gradient Boosting",
    "nb":  "Naive Bayes",
    "svc": "Linear SVC",
}


def _memory_usage() -> str:
    """Return process RSS without adding a production dependency."""
    try:
        with open("/proc/self/status", encoding="utf-8") as status_file:
            for line in status_file:
                if line.startswith("VmRSS:"):
                    return line.strip().replace("VmRSS:", "RSS:")
    except (FileNotFoundError, OSError):
        pass
    return "RSS: unavailable"


def _log_load_checkpoint(message: str) -> None:
    logger.info(
        f"[{datetime.now().isoformat(timespec='seconds')}] {message} | {_memory_usage()}"
    )

class FakeNewsPredictor:
    def __init__(self):
        self.vectorizer = None
        self.models: Dict[str, Any] = {}
        self.meta: Dict[str, Any] = {}
        self.loaded = False

    def load(self):
        """Load Phase 2 calibrated models and metadata from disk."""
        self.loaded = False
        _log_load_checkpoint("Starting calibrated artifact loading")
        models_dir = os.path.abspath(MODELS_DIR)
        report_path = os.path.abspath(PHASE2_REPORT_PATH)
        manifest_path = os.path.join(models_dir, "artifact_manifest.json")

        # Verify every byte before deserializing any pickle/joblib object.
        verify_artifact_bundle(models_dir, report_path, manifest_path)
        with open(report_path, encoding="utf-8") as report_file:
            report = json.load(report_file)

        vec_path = os.path.join(models_dir, "vectorizer.pkl")
        loaded_vectorizer = joblib.load(vec_path)
        loaded_models = {
            key: joblib.load(os.path.join(models_dir, f"{key}_calibrated.pkl"))
            for key in MODEL_KEYS
        }
        validate_loaded_bundle(loaded_vectorizer, loaded_models, report)

        self.vectorizer = loaded_vectorizer
        self.models = loaded_models
        self.meta = {}
        for key in MODEL_KEYS:
            model_report = report["models"][key]
            held_out = model_report["held_out"]
            selection = model_report["calibration_selection"]
            self.meta[key] = {
                "name": model_report["name"],
                "accuracy": round(float(held_out["accuracy"]) * 100, 2),
                "brier_score": held_out["brier_score"],
                "calibration_method": selection["selected_method"],
            }

        ensemble_report = report.get("ensemble", {})
        ensemble_held_out = ensemble_report.get("held_out", {})
        if ensemble_held_out:
            self.meta["ensemble"] = {
                "name": ensemble_report.get("name", "Calibrated ensemble"),
                "accuracy": round(float(ensemble_held_out["accuracy"]) * 100, 2),
                "brier_score": ensemble_held_out["brier_score"],
            }

        self.loaded = True
        _log_load_checkpoint(f"Completed calibrated artifact loading ({len(self.models)} models)")

    def predict(self, title: str = "", text: str = "") -> Dict[str, Any]:
        """
        Run ensemble prediction on input text.
        Returns dict with per-model predictions and ensemble result.
        """
        if not self.loaded:
            raise RuntimeError("Models not loaded. Call .load() first.")

        # Preprocess
        processed  = preprocess(title, text)
        vectorized = self.vectorizer.transform([processed])

        results = {}
        calibrated_probabilities = []

        for key, model in self.models.items():
            probability_class1 = extract_real_probability(model, vectorized)
            prediction = int(probability_class1 >= 0.5)
            confidence = probability_class1 if prediction == 1 else 1.0 - probability_class1
            calibrated_probabilities.append(probability_class1)

            results[key] = {
                "name":       MODEL_NAMES[key],
                "label":      "Fake" if prediction == 0 else "Real",
                "is_fake":    prediction == 0,
                # Confidence is the calibrated probability of the predicted class,
                # represented as a percentage to preserve the existing API shape.
                "confidence": round(confidence * 100, 1),
            }

        # ── Average calibrated P(class=1) ensemble ──────────────────────────────
        ensemble_probability = float(np.mean(calibrated_probabilities))
        if not np.isfinite(ensemble_probability) or not 0.0 <= ensemble_probability <= 1.0:
            raise RuntimeError("Ensemble probability is not finite or within [0, 1]")
        ensemble_is_real = ensemble_probability >= 0.5
        ensemble_fake = not ensemble_is_real
        ensemble_confidence = (
            ensemble_probability if ensemble_is_real else 1.0 - ensemble_probability
        )
        overall_confidence = round(ensemble_confidence * 100, 1)

        # Keep vote counts for display purposes
        fake_votes = sum(1 for r in results.values() if r["is_fake"])
        real_votes = len(results) - fake_votes

        return {
            "ensemble_is_fake":   ensemble_fake,
            "ensemble_label":     "FAKE NEWS" if ensemble_fake else "REAL NEWS",
            "overall_confidence": overall_confidence,
            "fake_votes":         fake_votes,
            "real_votes":         real_votes,
            "total_models":       len(self.models),
            "models":             results,
            "processed_length":   len(processed.split()),
        }

    def get_model_info(self) -> Dict:
        return self.meta


# Singleton instance
predictor = FakeNewsPredictor()
