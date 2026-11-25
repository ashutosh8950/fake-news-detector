import sys
import os
from pathlib import Path

import pytest


HARNESS_ROOT = Path(__file__).parents[1]
sys.path.insert(0, str(HARNESS_ROOT))

from isolated_build_harness import (  # noqa: E402
    PathSafetyError,
    ValidationGateError,
    build_group_split,
    record_output_plan,
    refuse_real_data_training,
    validate_build_configuration,
    validate_output_root,
)


def fixture_rows():
    # Eight independent groups, two same-label rows per group, alternating labels.
    groups = ["g0", "g0", "g1", "g1", "g2", "g2", "g3", "g3", "g4", "g4", "g5", "g5", "g6", "g6", "g7", "g7"]
    labels = [0, 0, 1, 1, 0, 0, 1, 1, 0, 0, 1, 1, 0, 0, 1, 1]
    return list(range(len(groups))), labels, groups


def synthetic_config():
    return {
        "candidate_id": "synthetic-001",
        "allow_real_data_training": False,
        "dataset_identity": "synthetic-fixture",
        "dataset_version": "v1",
        "dataset_schema": {"columns": ["feature"]},
        "source_data_hashes": {"synthetic": "sha256:test"},
        "label_mapping": {"0": "Fake", "1": "Real"},
        "licensing_evidence": {"status": "synthetic", "source": "test", "date": "2026-10-22"},
        "provenance_evidence": {"status": "synthetic", "source": "test", "date": "2026-10-22"},
        "source_revision": "synthetic",
        "preprocessing_revision": "synthetic",
        "grouping_policy": "synthetic-v1",
        "grouping_approval": {"status": "synthetic", "source": "test", "date": "2026-10-22"},
        "partition_manifest": {"status": "synthetic"},
        "estimator_config": {"kind": "synthetic"},
        "vectorizer_config": {"kind": "synthetic"},
        "calibration_config": {"kind": "synthetic"},
        "environment_record": {"python": "test"},
        "output_root": str(Path.cwd() / "synthetic-output"),
    }


def test_groups_are_disjoint_and_reported():
    features, labels, groups = fixture_rows()
    result = build_group_split(features, labels, groups)
    assert all(not overlap for overlap in result.report["group_overlap"].values())
    assert result.report["mixed_label_groups"] == []
    assert all(result.report[name]["rows"] > 0 for name in ("train", "selection", "calibration", "test"))
    assert all(result.report[name]["groups"] > 0 for name in ("train", "selection", "calibration", "test"))
    for group in set(groups):
        assert len({result.row_partitions[i] for i, value in enumerate(groups) if value == group}) == 1


def test_split_is_deterministic():
    fixture = fixture_rows()
    first = build_group_split(*fixture, seed=42)
    second = build_group_split(*fixture, seed=42)
    assert first.assignments == second.assignments
    assert first.row_partitions == second.row_partitions


@pytest.mark.parametrize("bad_groups", [["", *fixture_rows()[2][1:]], [None] * 16])
def test_invalid_group_ids_fail(bad_groups):
    features, labels, _ = fixture_rows()
    with pytest.raises(ValidationGateError, match="group_ids"):
        build_group_split(features, labels, bad_groups)


def test_invalid_labels_and_empty_partitions_fail():
    features, labels, groups = fixture_rows()
    labels[0] = 2
    with pytest.raises(ValidationGateError, match="labels"):
        build_group_split(features, labels, groups)
    with pytest.raises(ValidationGateError, match="at least four groups"):
        build_group_split([1, 2, 3], [0, 1, 0], ["only", "only", "only"])


def test_mixed_label_groups_are_explicitly_gated():
    features, labels, groups = fixture_rows()
    labels[1] = 1
    with pytest.raises(ValidationGateError, match="mixed-label"):
        build_group_split(features, labels, groups)
    result = build_group_split(features, labels, groups, allow_mixed_label_groups=True)
    assert "g0" in result.report["mixed_label_groups"]


def test_output_path_rejects_production_and_shared_evaluation(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "models" / "calibrated").mkdir(parents=True)
    (repo / "evaluation_results" / "old_report").mkdir(parents=True)
    namespace = repo / "evaluation_results" / "new_release_candidate" / "harness"
    with pytest.raises(PathSafetyError, match="allowed namespace"):
        validate_output_root(repo / "models" / "calibrated" / "candidate", repo, allowed_namespace=namespace)
    with pytest.raises(PathSafetyError, match="allowed"):
        validate_output_root(repo / "evaluation_results" / "old_report", repo, allowed_namespace=namespace)


def test_traversal_absolute_and_external_namespace_attempts_are_rejected(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    namespace = repo / "evaluation_results" / "new_release_candidate_2026-10-22" / "harness"
    with pytest.raises(PathSafetyError):
        validate_output_root(namespace / ".." / ".." / "old_report", repo, allowed_namespace=namespace)
    with pytest.raises(PathSafetyError, match="allowed namespace"):
        validate_output_root(tmp_path / "outside" / "candidate", repo, allowed_namespace=tmp_path / "outside")
    with pytest.raises(PathSafetyError, match="allowed namespace"):
        validate_output_root(namespace / "candidate", repo, allowed_namespace=repo / "models")


def test_symlink_alias_to_protected_path_is_rejected_when_supported(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    models = repo / "models"
    models.mkdir()
    namespace = repo / "evaluation_results" / "new_release_candidate_2026-10-22" / "harness"
    namespace.mkdir(parents=True)
    alias = namespace / "alias"
    try:
        os.symlink(models, alias, target_is_directory=True)
    except (OSError, NotImplementedError) as exc:
        pytest.skip(f"directory symlink unavailable in this environment: {exc}")
    with pytest.raises(PathSafetyError):
        validate_output_root(alias / "candidate", repo, allowed_namespace=namespace)


def test_injected_resolver_exercising_containment_rejects_external_alias(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    namespace = repo / "evaluation_results" / "new_release_candidate_2026-10-22" / "harness"
    alias = namespace / "alias"
    outside = tmp_path / "outside"
    outside.mkdir()
    real_resolve = __import__("isolated_build_harness")._resolved

    def simulated_resolver(path):
        resolved = real_resolve(path)
        if resolved == alias / "candidate":
            return outside / "candidate"
        return resolved

    with pytest.raises(PathSafetyError, match="inside the explicitly allowed"):
        validate_output_root(alias / "candidate", repo, allowed_namespace=namespace, path_resolver=simulated_resolver)


def test_failed_validation_creates_no_artifacts(tmp_path):
    repo = tmp_path / "repo"
    namespace = repo / "evaluation_results" / "new_release_candidate_2026-10-22" / "harness"
    existing = namespace / "already-used"
    existing.mkdir(parents=True)
    sentinel = existing / "sentinel.txt"
    sentinel.write_text("preserve", encoding="utf-8")
    with pytest.raises(PathSafetyError, match="already exists"):
        record_output_plan(existing, repo, {}, allowed_namespace=namespace)
    assert sentinel.read_text(encoding="utf-8") == "preserve"
    assert not (existing / "artifacts").exists()


def test_real_data_training_refuses_unresolved_provenance_without_writing():
    config = {"candidate_id": "synthetic-test", "allow_real_data_training": False}
    with pytest.raises(ValidationGateError, match="missing mandatory build fields") as error:
        refuse_real_data_training(config)
    assert "secret" not in str(error.value).lower()


def test_plan_records_paths_before_future_training(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    namespace = repo / "evaluation_results" / "new_release_candidate_2026-10-22" / "harness"
    output = namespace / "candidate-001"
    config = synthetic_config()
    config["output_root"] = str(output)
    paths = record_output_plan(output, repo, config, allowed_namespace=namespace, synthetic=True)
    assert set(paths) == {"training_plan", "split_manifest", "validation_report", "artifacts_directory"}
    assert (output / "training_plan.json").exists()
    assert not (output / "artifacts").exists()


def test_split_configuration_rejects_invalid_target_fractions():
    features, labels, groups = fixture_rows()
    with pytest.raises(ValidationGateError, match="target_fractions"):
        build_group_split(features, labels, groups, target_fractions={name: 0.25 for name in ("train", "selection", "calibration")})


def test_configuration_rejects_types_unknown_fields_and_contradictions():
    config = synthetic_config()
    config["allow_real_data_training"] = "yes"
    with pytest.raises(ValidationGateError, match="boolean"):
        validate_build_configuration(config, synthetic=True)
    config = synthetic_config()
    config["unexpected"] = "value"
    with pytest.raises(ValidationGateError, match="unexpected"):
        validate_build_configuration(config, synthetic=True)
    config = synthetic_config()
    config["allow_real_data_training"] = True
    with pytest.raises(ValidationGateError, match="synthetic"):
        validate_build_configuration(config, synthetic=True)
    config = synthetic_config()
    config["candidate_id"] = "../escape"
    with pytest.raises(ValidationGateError, match="identifier"):
        validate_build_configuration(config, synthetic=True)


def test_unresolved_real_provenance_cannot_be_bypassed_by_flag():
    config = synthetic_config()
    config["allow_real_data_training"] = True
    config["licensing_evidence"] = {"status": "unresolved", "source": "manual", "date": "2026-10-22"}
    config["provenance_evidence"] = {"status": "unresolved", "source": "manual", "date": "2026-10-22"}
    with pytest.raises(ValidationGateError, match="reviewed licensing_evidence"):
        refuse_real_data_training(config)


def test_real_training_requires_group_approval_and_partition_manifest():
    config = synthetic_config()
    config["allow_real_data_training"] = True
    config["licensing_evidence"] = {"status": "reviewed", "source": "owner-record", "date": "2026-10-22"}
    config["provenance_evidence"] = {"status": "reviewed", "source": "owner-record", "date": "2026-10-22"}
    config["grouping_approval"] = {"status": "unresolved", "source": "manual", "date": "2026-10-22"}
    with pytest.raises(ValidationGateError, match="reviewed grouping_approval"):
        refuse_real_data_training(config)


def test_plan_write_failure_cleans_new_directory(tmp_path, monkeypatch):
    repo = tmp_path / "repo"
    repo.mkdir()
    namespace = repo / "evaluation_results" / "new_release_candidate_2026-10-22" / "harness"
    output = namespace / "candidate-failure"
    original = Path.write_text

    def fail_plan(path, *args, **kwargs):
        if path.name == "training_plan.json":
            raise OSError("simulated plan write failure")
        return original(path, *args, **kwargs)

    monkeypatch.setattr(Path, "write_text", fail_plan)
    config = synthetic_config()
    config["output_root"] = str(output)
    with pytest.raises(OSError, match="simulated"):
        record_output_plan(output, repo, config, allowed_namespace=namespace, synthetic=True)
    assert not output.exists()
