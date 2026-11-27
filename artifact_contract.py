"""Fail-closed artifact and probability contracts for production inference."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

import numpy as np

ARTIFACT_MANIFEST_SCHEMA = "truthscan_artifact_manifest_v1"
REQUIRED_MODEL_FILES = (
    "lr_calibrated.pkl",
    "dt_calibrated.pkl",
    "gbc_calibrated.pkl",
    "nb_calibrated.pkl",
    "svc_calibrated.pkl",
)
REQUIRED_MODEL_KEYS = ("lr", "dt", "gbc", "nb", "svc")
REQUIRED_ARTIFACT_FILES = ("vectorizer.pkl", *REQUIRED_MODEL_FILES, "phase2_calibration_report.json")
MAX_ARTIFACT_BYTES = 256 * 1024 * 1024


class ArtifactVerificationError(RuntimeError):
    """Raised when an artifact bundle cannot be trusted or validated."""


class PredictionContractError(RuntimeError):
    """Raised when an estimator violates the production probability contract."""


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _load_manifest(manifest_path: Path) -> dict[str, Any]:
    if not manifest_path.is_file():
        raise ArtifactVerificationError("Trusted artifact manifest is missing")
    try:
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ArtifactVerificationError("Trusted artifact manifest is unreadable") from exc
    if not isinstance(payload, dict) or payload.get("schema_version") != ARTIFACT_MANIFEST_SCHEMA:
        raise ArtifactVerificationError("Trusted artifact manifest schema is invalid")
    artifacts = payload.get("artifacts")
    if not isinstance(artifacts, dict) or set(artifacts) != set(REQUIRED_ARTIFACT_FILES):
        raise ArtifactVerificationError("Trusted artifact manifest entries are incomplete or unexpected")
    for name, record in artifacts.items():
        if Path(name).name != name or Path(name).is_absolute() or not isinstance(record, dict):
            raise ArtifactVerificationError(f"Invalid artifact manifest entry: {name}")
        digest = record.get("sha256")
        size = record.get("size_bytes")
        if not isinstance(digest, str) or len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest.lower()):
            raise ArtifactVerificationError(f"Invalid SHA-256 for {name}")
        if not isinstance(size, int) or size < 0 or size > MAX_ARTIFACT_BYTES:
            raise ArtifactVerificationError(f"Invalid size for {name}")
    return payload


def verify_artifact_bundle(models_dir: Path, report_path: Path, manifest_path: Path | None = None) -> dict[str, Any]:
    """Verify all bytes before any pickle/joblib deserialization occurs."""
    models_dir = Path(models_dir)
    report_path = Path(report_path)
    manifest_path = Path(manifest_path or models_dir / "artifact_manifest.json")
    manifest = _load_manifest(manifest_path)
    for name in REQUIRED_ARTIFACT_FILES:
        path = report_path if name == "phase2_calibration_report.json" else models_dir / name
        if not path.is_file():
            raise ArtifactVerificationError(f"Required artifact is missing: {name}")
        size = path.stat().st_size
        record = manifest["artifacts"][name]
        if size != record["size_bytes"] or size > MAX_ARTIFACT_BYTES:
            raise ArtifactVerificationError(f"Artifact size mismatch: {name}")
        if sha256_file(path) != record["sha256"]:
            raise ArtifactVerificationError(f"Artifact SHA-256 mismatch: {name}")
    return manifest


def validate_loaded_bundle(vectorizer: Any, models: Mapping[str, Any], report: Mapping[str, Any]) -> None:
    """Validate interfaces and compatibility after integrity verification."""
    if not hasattr(vectorizer, "transform"):
        raise ArtifactVerificationError("Vectorizer lacks transform()")
    try:
        feature_probe = vectorizer.transform([""])
        feature_count = int(feature_probe.shape[1])
    except Exception as exc:
        raise ArtifactVerificationError("Vectorizer feature probe failed") from exc
    if feature_count <= 0:
        raise ArtifactVerificationError("Vectorizer has no features")
    if set(models) != set(REQUIRED_MODEL_KEYS):
        raise ArtifactVerificationError("Loaded model set is incomplete or unexpected")
    report_models = report.get("models") if isinstance(report, Mapping) else None
    if not isinstance(report_models, Mapping) or set(report_models) != set(REQUIRED_MODEL_KEYS):
        raise ArtifactVerificationError("Calibration report model set is incomplete or unexpected")
    for key, model in models.items():
        try:
            validate_probability_contract(model, feature_count)
            if hasattr(model, "n_features_in_") and int(model.n_features_in_) != feature_count:
                raise ValueError("feature dimension does not match vectorizer")
        except (PredictionContractError, TypeError, ValueError) as exc:
            raise ArtifactVerificationError(f"Loaded model contract is invalid for {key}") from exc


def validate_probability_contract(model: Any, feature_count: int | None = None) -> int:
    """Validate labels and return the column containing class 1 (Real)."""
    classes = getattr(model, "classes_", None)
    if classes is None:
        raise PredictionContractError("Estimator is missing classes_")
    try:
        labels = list(classes)
    except TypeError as exc:
        raise PredictionContractError("Estimator classes_ is not iterable") from exc
    if len(labels) != 2 or set(labels) != {0, 1}:
        raise PredictionContractError("Estimator classes_ must contain exactly the labels 0 and 1")
    if not callable(getattr(model, "predict_proba", None)):
        raise PredictionContractError("Estimator lacks predict_proba()")
    if feature_count is not None and hasattr(model, "n_features_in_") and int(model.n_features_in_) != feature_count:
        raise PredictionContractError("Estimator feature dimension does not match vectorizer")
    return labels.index(1)


def extract_real_probability(model: Any, features: Any) -> float:
    """Extract and validate P(Real) from a single-row estimator output."""
    real_index = validate_probability_contract(model)
    try:
        output = np.asarray(model.predict_proba(features), dtype=float)
    except Exception as exc:
        raise PredictionContractError("Estimator probability prediction failed") from exc
    if output.ndim != 2 or output.shape[0] != 1 or output.shape[1] != 2:
        raise PredictionContractError("Estimator probability output must have shape (1, 2)")
    if not np.isfinite(output).all() or ((output < 0.0) | (output > 1.0)).any():
        raise PredictionContractError("Estimator probabilities are not finite or within [0, 1]")
    probability = float(output[0, real_index])
    return probability
