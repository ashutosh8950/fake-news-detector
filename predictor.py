"""
Ensemble prediction engine for Fake News Detection.
Loads all 5 trained models and produces:
  - Per-model predictions + probabilities
  - Ensemble majority vote
  - Overall confidence score
"""

import os
import json
import joblib
import numpy as np
from typing import Dict, Any

from preprocessor import preprocess

MODELS_DIR = "models"

MODEL_KEYS = ["lr", "dt", "gbc", "rfc", "nb"]
MODEL_NAMES = {
    "lr":  "Logistic Regression",
    "dt":  "Decision Tree",
    "gbc": "Gradient Boosting",
    "rfc": "Random Forest",
    "nb":  "Naive Bayes",
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
        print(f"✅ Loaded {len(self.models)} models")

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
        fake_votes = 0

        for key, model in self.models.items():
            prediction = int(model.predict(vectorized)[0])
            # Get probability if supported
            if hasattr(model, "predict_proba"):
                proba = model.predict_proba(vectorized)[0]
                confidence = float(proba[prediction])
            else:
                confidence = 1.0 if prediction == 1 else 0.0

            if prediction == 0:
                fake_votes += 1

            results[key] = {
                "name":       MODEL_NAMES[key],
                "label":      "Fake" if prediction == 0 else "Real",
                "is_fake":    prediction == 0,
                "confidence": round(confidence * 100, 1),
            }

        # Ensemble: majority vote
        total_models   = len(self.models)
        real_votes     = total_models - fake_votes
        ensemble_fake  = fake_votes > real_votes

        # Weighted ensemble confidence (based on model accuracy weights)
        weights = {k: self.meta.get(k, {}).get("accuracy", 70) for k in self.models}
        total_w = sum(weights.values())
        weighted_fake_score = sum(
            weights[k] for k in self.models
            if results[k]["is_fake"]
        ) / total_w

        overall_confidence = round(
            (weighted_fake_score if ensemble_fake else (1 - weighted_fake_score)) * 100, 1
        )

        return {
            "ensemble_is_fake":   ensemble_fake,
            "ensemble_label":     "FAKE NEWS" if ensemble_fake else "REAL NEWS",
            "overall_confidence": overall_confidence,
            "fake_votes":         fake_votes,
            "real_votes":         real_votes,
            "total_models":       total_models,
            "models":             results,
            "processed_length":   len(processed.split()),
        }

    def get_model_info(self) -> Dict:
        return self.meta


# Singleton instance
predictor = FakeNewsPredictor()
