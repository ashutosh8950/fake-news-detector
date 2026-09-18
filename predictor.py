"""
Ensemble prediction engine for Fake News Detection.
Loads all 6 Phase 2 calibrated models and produces:
  - Per-model predictions + calibrated probabilities
  - Average-probability ensemble using calibrated P(class=1) values
  - Overall confidence = calibrated probability of the predicted class, as a percentage
"""

import os
import json
import joblib
import numpy as np
from typing import Dict, Any

from loguru import logger

from preprocessor import preprocess
from config import settings

MODELS_DIR = os.path.join(settings.models_dir, "calibrated")
PHASE2_REPORT_PATH = os.path.join("evaluation_results", "phase2_calibration_report.json")

MODEL_KEYS = ["lr", "dt", "gbc", "rfc", "nb", "svc"]
MODEL_NAMES = {
    "lr":  "Logistic Regression",
    "dt":  "Decision Tree",
    "gbc": "Gradient Boosting",
    "rfc": "Random Forest",
    "nb":  "Naive Bayes",
    "svc": "Linear SVC",
}

class FakeNewsPredictor:
    def __init__(self):
        self.vectorizer = None
        self.models: Dict[str, Any] = {}
        self.meta: Dict[str, Any] = {}
        self.loaded = False

    def load(self):
        """Load Phase 2 calibrated models and metadata from disk."""
        vec_path  = os.path.join(MODELS_DIR, "vectorizer.pkl")

        if not os.path.exists(vec_path):
            raise FileNotFoundError(
                "Calibrated models not found. Please run: python phase2_calibration.py"
            )

        self.vectorizer = joblib.load(vec_path)

        self.models = {}
        for key in MODEL_KEYS:
            model_path = os.path.join(MODELS_DIR, f"{key}_calibrated.pkl")
            if not os.path.exists(model_path):
                raise FileNotFoundError(f"Calibrated model not found: {model_path}")
            self.models[key] = joblib.load(model_path)

        if not os.path.exists(PHASE2_REPORT_PATH):
            raise FileNotFoundError(
                f"Phase 2 calibration report not found: {PHASE2_REPORT_PATH}"
            )

        # The deprecated models/model_meta.json described contaminated artifacts.
        # Production metadata now comes from the Phase 2 held-out evaluation report.
        with open(PHASE2_REPORT_PATH, encoding="utf-8") as report_file:
            report = json.load(report_file)

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
        logger.info(f"✅ Loaded {len(self.models)} models")

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
            if not hasattr(model, "predict_proba"):
                raise TypeError(f"Calibrated model {key} does not support predict_proba()")

            probability_class1 = float(model.predict_proba(vectorized)[0][1])
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
