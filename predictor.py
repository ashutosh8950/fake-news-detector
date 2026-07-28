"""
Ensemble prediction engine for Fake News Detection.
Loads all 6 trained models and produces:
  - Per-model predictions + probabilities
  - Accuracy-WEIGHTED ensemble (no ties possible)
  - Overall confidence = winner weight share as percentage
  - LinearSVC uses decision_function (sigmoid-scaled) for confidence
"""

import os
import json
import joblib
import numpy as np
from typing import Dict, Any

from loguru import logger

from preprocessor import preprocess
from config import settings

MODELS_DIR = settings.models_dir

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
        """Load all models from disk (called once at startup)."""
        vec_path  = os.path.join(MODELS_DIR, "vectorizer.pkl")
        meta_path = os.path.join(MODELS_DIR, "model_meta.json")

        if not os.path.exists(vec_path):
            raise FileNotFoundError(
                "Models not found. Please run: python train.py"
            )

        self.vectorizer = joblib.load(vec_path)

        for key in MODEL_KEYS:
            model_path = os.path.join(MODELS_DIR, f"{key}_model.pkl")
            if os.path.exists(model_path):
                self.models[key] = joblib.load(model_path)

        if os.path.exists(meta_path):
            with open(meta_path) as f:
                self.meta = json.load(f)

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
        fake_weight_sum = 0.0
        real_weight_sum = 0.0

        # Build per-model accuracy weights (fallback 70 if not in meta)
        weights = {k: self.meta.get(k, {}).get("accuracy", 70.0) for k in self.models}

        for key, model in self.models.items():
            prediction = int(model.predict(vectorized)[0])
            # Get probability if supported (predict_proba)
            if hasattr(model, "predict_proba"):
                proba = model.predict_proba(vectorized)[0]
                confidence = float(proba[prediction])
            # LinearSVC: use decision_function score, sigmoid-scaled to 0-1
            elif hasattr(model, "decision_function"):
                score = float(model.decision_function(vectorized)[0])
                # sigmoid: maps (-inf,+inf) -> (0,1)
                # score > 0 means class 1 (Real), score < 0 means class 0 (Fake)
                sigmoid = 1.0 / (1.0 + np.exp(-abs(score)))
                confidence = sigmoid
            else:
                confidence = 1.0 if prediction == 1 else 0.0

            # Accumulate weighted scores
            w = weights[key]
            if prediction == 0:   # Fake
                fake_weight_sum += w
            else:                 # Real
                real_weight_sum += w

            results[key] = {
                "name":       MODEL_NAMES[key],
                "label":      "Fake" if prediction == 0 else "Real",
                "is_fake":    prediction == 0,
                "confidence": round(confidence * 100, 1),
            }

        # ── Weighted ensemble decision (ties mathematically impossible) ─────────
        total_weight  = fake_weight_sum + real_weight_sum
        ensemble_fake = fake_weight_sum > real_weight_sum
        winner_score  = fake_weight_sum if ensemble_fake else real_weight_sum

        # Confidence = winner's share of total accuracy weight
        overall_confidence = round((winner_score / total_weight) * 100, 1)

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
