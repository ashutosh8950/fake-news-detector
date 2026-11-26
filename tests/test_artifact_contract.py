import hashlib
import json

import numpy as np
import pytest

import predictor
from artifact_contract import (
    REQUIRED_ARTIFACT_FILES,
    ArtifactVerificationError,
    PredictionContractError,
    extract_real_probability,
    validate_loaded_bundle,
    validate_probability_contract,
    verify_artifact_bundle,
)


class SyntheticEstimator:
    def __init__(self, classes=(0, 1), probabilities=(0.25, 0.75)):
        self.classes_ = np.array(classes)
        self.probabilities = np.array([probabilities], dtype=float)
        self.n_features_in_ = 3

    def predict_proba(self, features):
        return self.probabilities


class SyntheticVectorizer:
    def transform(self, values):
        return np.zeros((len(values), 3))


def write_bundle(tmp_path, *, manifest=True, records=None):
    models = tmp_path / "models"
    metadata = tmp_path / "metadata"
    models.mkdir(parents=True)
    metadata.mkdir(parents=True)
    paths = {}
    for name in REQUIRED_ARTIFACT_FILES:
        path = metadata / name if name == "phase2_calibration_report.json" else models / name
        path.write_bytes(name.encode("utf-8"))
        paths[name] = path
    if manifest:
        artifacts = records or {
            name: {"sha256": hashlib.sha256(path.read_bytes()).hexdigest(), "size_bytes": path.stat().st_size}
            for name, path in paths.items()
        }
        (models / "artifact_manifest.json").write_text(
            json.dumps({"schema_version": "truthscan_artifact_manifest_v1", "artifacts": artifacts}),
            encoding="utf-8",
        )
    return models, metadata


def test_real_probability_uses_class_label_for_both_orders():
    assert extract_real_probability(SyntheticEstimator((0, 1), (0.25, 0.75)), None) == 0.75
    assert extract_real_probability(SyntheticEstimator((1, 0), (0.75, 0.25)), None) == 0.75


@pytest.mark.parametrize(
    "estimator",
    [
        SyntheticEstimator((0,)),
        SyntheticEstimator((0, 2)),
        SyntheticEstimator((0, 0)),
        object(),
    ],
)
def test_invalid_class_or_probability_interface_is_rejected(estimator):
    with pytest.raises(PredictionContractError):
        validate_probability_contract(estimator)


@pytest.mark.parametrize("probabilities", [(0.1,), (0.1, 0.2, 0.7), (np.nan, 0.5), (np.inf, 0.5), (-0.1, 1.1)])
def test_invalid_probability_shape_or_values_are_rejected(probabilities):
    with pytest.raises(PredictionContractError):
        extract_real_probability(SyntheticEstimator((0, 1), probabilities), None)


def test_hash_verification_accepts_exact_synthetic_bundle(tmp_path):
    models, metadata = write_bundle(tmp_path)
    manifest = verify_artifact_bundle(models, metadata / "phase2_calibration_report.json")
    assert manifest["schema_version"] == "truthscan_artifact_manifest_v1"


def test_hash_mismatch_is_rejected_before_deserialization(tmp_path, monkeypatch):
    models, metadata = write_bundle(tmp_path)
    (models / "dt_calibrated.pkl").write_bytes(b"tampered")
    called = False

    def fail_if_called(_):
        nonlocal called
        called = True
        raise AssertionError("deserializer must not be called")

    monkeypatch.setattr(predictor.joblib, "load", fail_if_called)
    monkeypatch.setattr(predictor, "MODELS_DIR", str(models))
    monkeypatch.setattr(predictor, "PHASE2_REPORT_PATH", str(metadata / "phase2_calibration_report.json"))
    with pytest.raises(ArtifactVerificationError):
        predictor.FakeNewsPredictor().load()
    assert called is False


def test_missing_or_malformed_manifest_is_rejected(tmp_path):
    models, metadata = write_bundle(tmp_path, manifest=False)
    with pytest.raises(ArtifactVerificationError):
        verify_artifact_bundle(models, metadata / "phase2_calibration_report.json")
    (models / "artifact_manifest.json").write_text("not-json", encoding="utf-8")
    with pytest.raises(ArtifactVerificationError):
        verify_artifact_bundle(models, metadata / "phase2_calibration_report.json")


def test_manifest_rejects_missing_and_unexpected_entries(tmp_path):
    models, metadata = write_bundle(tmp_path)
    manifest_path = models / "artifact_manifest.json"
    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    payload["artifacts"].pop("dt_calibrated.pkl")
    manifest_path.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(ArtifactVerificationError):
        verify_artifact_bundle(models, metadata / "phase2_calibration_report.json")
    models, metadata = write_bundle(tmp_path / "second")
    manifest_path = models / "artifact_manifest.json"
    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    payload["artifacts"]["unexpected.pkl"] = payload["artifacts"]["vectorizer.pkl"]
    manifest_path.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(ArtifactVerificationError):
        verify_artifact_bundle(models, metadata / "phase2_calibration_report.json")


def test_loaded_bundle_contract_checks_model_set_and_feature_dimensions():
    models = {key: SyntheticEstimator() for key in ("lr", "dt", "gbc", "nb", "svc")}
    report = {"models": {key: {} for key in models}}
    validate_loaded_bundle(SyntheticVectorizer(), models, report)

    models["svc"].n_features_in_ = 4
    with pytest.raises(ArtifactVerificationError):
        validate_loaded_bundle(SyntheticVectorizer(), models, report)
