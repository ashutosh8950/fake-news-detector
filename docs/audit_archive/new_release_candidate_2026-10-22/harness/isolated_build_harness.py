"""Safety gates for a future TruthScan candidate build.

This module deliberately does not import training, preprocessing, spaCy, joblib,
pickle, or the production predictor. It only validates configuration, plans
safe output paths, and creates deterministic synthetic-data group partitions.
Real-data training is refused until provenance and licensing evidence are
explicitly supplied outside this module.
"""

from __future__ import annotations

import hashlib
import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence


PARTITIONS = ("train", "selection", "calibration", "test")
ALLOWED_LABELS = frozenset({0, 1})
REQUIRED_PROVENANCE = (
    "dataset_identity",
    "dataset_version",
    "dataset_schema",
    "source_data_hashes",
    "label_mapping",
    "licensing_evidence",
    "provenance_evidence",
    "source_revision",
    "preprocessing_revision",
    "grouping_policy",
    "grouping_approval",
    "partition_manifest",
    "estimator_config",
    "vectorizer_config",
    "calibration_config",
    "environment_record",
    "candidate_id",
)
ALLOWED_CONFIG_KEYS = frozenset(REQUIRED_PROVENANCE) | frozenset({"allow_real_data_training", "output_root"})
STRUCTURED_CONFIG_KEYS = frozenset({"dataset_schema", "label_mapping", "estimator_config", "vectorizer_config", "calibration_config", "environment_record", "source_data_hashes", "partition_manifest"})


class HarnessError(ValueError):
    """Base class for fail-closed harness errors."""


class PathSafetyError(HarnessError):
    """Raised when an output path is not demonstrably isolated."""


class ValidationGateError(HarnessError):
    """Raised when a mandatory build or split gate is not met."""


@dataclass(frozen=True)
class GroupSplit:
    assignments: dict[str, str]
    row_partitions: tuple[str, ...]
    report: dict[str, Any]


def _resolved(path: os.PathLike[str] | str) -> Path:
    return Path(path).expanduser().resolve(strict=False)


def _is_relative_to(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
        return True
    except ValueError:
        return False


def validate_output_root(
    output_root: os.PathLike[str] | str,
    repo_root: os.PathLike[str] | str,
    *,
    allowed_namespace: os.PathLike[str] | str | None = None,
    path_resolver: Any | None = None,
) -> Path:
    """Validate a future output root before any training-side effect.

    The root must be explicit, absolute after resolution, inside the designated
    new namespace, and outside production/shared evaluation paths. Existing
    files are rejected so a candidate cannot silently overwrite prior evidence.
    """

    if output_root is None or str(output_root).strip() == "":
        raise PathSafetyError("output_root is required and cannot be empty")
    resolver = path_resolver or _resolved
    repo = resolver(repo_root)
    if not repo.is_dir():
        raise PathSafetyError("repo_root must resolve to an existing directory")
    root = resolver(output_root)
    designated_namespace = repo / "evaluation_results" / "new_release_candidate_2026-10-22" / "harness"
    namespace = resolver(allowed_namespace) if allowed_namespace else designated_namespace
    if not _is_relative_to(namespace, designated_namespace):
        raise PathSafetyError("allowed namespace must remain inside the designated new candidate harness namespace")
    protected_models = repo / "models"
    protected_evaluations = repo / "evaluation_results"
    if not _is_relative_to(root, namespace):
        raise PathSafetyError("output_root must be inside the explicitly allowed new candidate namespace")
    if _is_relative_to(root, protected_models):
        raise PathSafetyError("production model paths are not allowed")
    if root == protected_evaluations or root == protected_models:
        raise PathSafetyError("shared repository roots are not allowed")
    if root.exists():
        raise PathSafetyError("output_root already exists; refusing overwrite")
    return root


def planned_output_paths(output_root: os.PathLike[str] | str) -> dict[str, str]:
    root = _resolved(output_root)
    return {
        "training_plan": str(root / "training_plan.json"),
        "split_manifest": str(root / "split_manifest.json"),
        "validation_report": str(root / "validation_report.json"),
        "artifacts_directory": str(root / "artifacts"),
    }


def record_output_plan(
    output_root: os.PathLike[str] | str,
    repo_root: os.PathLike[str] | str,
    config: Mapping[str, Any],
    *,
    allowed_namespace: os.PathLike[str] | str | None = None,
    synthetic: bool = False,
) -> dict[str, str]:
    """Create an empty candidate directory and record paths before training."""

    root = validate_output_root(output_root, repo_root, allowed_namespace=allowed_namespace)
    validate_build_configuration(config, synthetic=synthetic)
    configured_root = _resolved(config["output_root"])
    if configured_root != root:
        raise PathSafetyError("configuration output_root does not match the validated output root")
    root.mkdir(parents=True, exist_ok=False)
    paths = planned_output_paths(root)
    plan_path = root / "training_plan.json"
    try:
        plan_path.write_text(
            json.dumps({"status": "planned_only", "paths": paths, "config": dict(config)}, indent=2, sort_keys=True),
            encoding="utf-8",
        )
    except Exception:
        # Best-effort cleanup of only the directory created by this call. This
        # is not a guarantee against filesystem races.
        try:
            plan_path.unlink(missing_ok=True)
            root.rmdir()
        except OSError:
            pass
        raise
    return paths


def _require_nonempty_strings(values: Sequence[Any], name: str) -> None:
    if any(not isinstance(value, str) or not value.strip() for value in values):
        raise ValidationGateError(f"{name} must contain only non-empty strings")


def _group_sort_key(seed: int, group_id: str) -> str:
    return hashlib.sha256(f"{seed}:{group_id}".encode("utf-8")).hexdigest()


def _counts(rows: Sequence[tuple[int, str]], assignments: Mapping[str, str]) -> dict[str, dict[str, Any]]:
    result = {p: {"rows": 0, "groups": 0, "class_counts": {"0": 0, "1": 0}, "group_ids": []} for p in PARTITIONS}
    for group_id, partition in assignments.items():
        result[partition]["groups"] += 1
        result[partition]["group_ids"].append(group_id)
    for label, group_id in rows:
        if group_id not in assignments:
            continue
        partition = assignments[group_id]
        result[partition]["rows"] += 1
        result[partition]["class_counts"][str(label)] += 1
    for value in result.values():
        value["group_ids"].sort()
    return result


def build_group_split(
    features: Sequence[Any],
    labels: Sequence[Any],
    group_ids: Sequence[Any],
    *,
    seed: int = 42,
    target_fractions: Mapping[str, float] | None = None,
    require_each_class: bool = True,
    allow_mixed_label_groups: bool = False,
) -> GroupSplit:
    """Build a deterministic, greedy group split without claiming optimality."""

    if not isinstance(seed, int):
        raise ValidationGateError("seed must be an integer")
    if not (len(features) == len(labels) == len(group_ids)) or not features:
        raise ValidationGateError("features, labels, and group_ids must have the same non-zero length")
    _require_nonempty_strings(list(group_ids), "group_ids")
    if any(label not in ALLOWED_LABELS or isinstance(label, bool) for label in labels):
        raise ValidationGateError("labels must be integer values 0 or 1")
    fractions = dict(target_fractions or {"train": 0.60, "selection": 0.15, "calibration": 0.15, "test": 0.10})
    if tuple(fractions) != PARTITIONS or any(float(fractions[p]) <= 0 for p in PARTITIONS) or abs(sum(float(fractions[p]) for p in PARTITIONS) - 1.0) > 1e-9:
        raise ValidationGateError("target_fractions must contain positive train/selection/calibration/test values summing to 1")

    groups: dict[str, list[int]] = {}
    for index, group_id in enumerate(group_ids):
        groups.setdefault(group_id, []).append(index)
    if len(groups) < len(PARTITIONS):
        raise ValidationGateError("at least four groups are required for non-empty partitions")
    mixed = sorted(group_id for group_id, indexes in groups.items() if len({labels[i] for i in indexes}) > 1)
    if mixed and not allow_mixed_label_groups:
        raise ValidationGateError("mixed-label groups require explicit allow_mixed_label_groups=True")
    total_rows = len(labels)
    target_rows = {p: total_rows * float(fractions[p]) for p in PARTITIONS}
    assignments: dict[str, str] = {}
    group_items = sorted(groups.items(), key=lambda item: _group_sort_key(seed, item[0]))
    if require_each_class:
        # Reserve deterministic class coverage before balancing row totals.
        # This is a feasibility guard, not an optimization claim.
        available = {group_id for group_id, _ in group_items}
        for partition in PARTITIONS:
            covered: set[int] = set()
            for required_label in (0, 1):
                if required_label in covered:
                    continue
                candidates = [
                    (group_id, indexes)
                    for group_id, indexes in group_items
                    if group_id in available and any(labels[i] == required_label for i in indexes)
                ]
                if not candidates:
                    raise ValidationGateError("not enough class-bearing groups for required partition coverage")
                if allow_mixed_label_groups and not covered:
                    candidates.sort(
                        key=lambda item: (
                            not ({labels[i] for i in item[1]} >= ALLOWED_LABELS),
                            _group_sort_key(seed, item[0]),
                        )
                    )
                group_id, _ = candidates[0]
                assignments[group_id] = partition
                available.remove(group_id)
                covered.update(labels[i] for i in groups[group_id])
    # Place larger groups first, with a stable hash tie-breaker. This is a
    # deterministic heuristic, not a global optimization algorithm.
    group_items.sort(key=lambda item: (-len(item[1]), _group_sort_key(seed, item[0])))
    for group_id, indexes in group_items:
        if group_id in assignments:
            continue
        group_counts = {label: sum(1 for i in indexes if labels[i] == label) for label in (0, 1)}
        candidates: list[tuple[float, str]] = []
        current = _counts([(int(labels[i]), group_ids[i]) for i in range(total_rows)], assignments)
        for partition in PARTITIONS:
            score = 0.0
            for candidate_partition in PARTITIONS:
                rows_after = current[candidate_partition]["rows"] + (len(indexes) if candidate_partition == partition else 0)
                score += abs(rows_after - target_rows[candidate_partition])
                for label in (0, 1):
                    desired = total_rows * float(fractions[candidate_partition]) * sum(1 for value in labels if value == label) / total_rows
                    observed = current[candidate_partition]["class_counts"][str(label)] + (group_counts[label] if candidate_partition == partition else 0)
                    score += abs(observed - desired)
            # Prefer an empty partition while there are fewer than four groups.
            if current[partition]["groups"] == 0:
                score -= total_rows
            candidates.append((score, partition))
        _, selected = min(candidates, key=lambda item: (item[0], PARTITIONS.index(item[1])))
        assignments[group_id] = selected

    rows = [(int(label), group_id) for label, group_id in zip(labels, group_ids)]
    report = _counts(rows, assignments)
    overlaps = {f"{left}:{right}": sorted(set(report[left]["group_ids"]) & set(report[right]["group_ids"])) for left in PARTITIONS for right in PARTITIONS if left < right}
    if any(report[p]["groups"] == 0 or report[p]["rows"] == 0 for p in PARTITIONS):
        raise ValidationGateError("split produced an empty partition")
    if require_each_class and any(report[p]["class_counts"]["0"] == 0 or report[p]["class_counts"]["1"] == 0 for p in PARTITIONS):
        raise ValidationGateError("split produced a partition without both required classes")
    if any(overlaps.values()):
        raise ValidationGateError("group overlap detected between partitions")
    report["mixed_label_groups"] = mixed
    report["group_overlap"] = overlaps
    report["seed"] = seed
    report["target_fractions"] = {p: float(fractions[p]) for p in PARTITIONS}
    report["algorithm"] = "deterministic_greedy_group_split_v1; not globally optimal"
    row_partitions = tuple(assignments[group_id] for group_id in group_ids)
    return GroupSplit(assignments=assignments, row_partitions=row_partitions, report=report)


def validate_build_configuration(config: Mapping[str, Any], *, synthetic: bool = False) -> None:
    if not isinstance(config, Mapping):
        raise ValidationGateError("configuration must be a mapping")
    unexpected = sorted(set(config) - ALLOWED_CONFIG_KEYS)
    if unexpected:
        raise ValidationGateError("unexpected configuration fields: " + ", ".join(unexpected))
    if not isinstance(config.get("allow_real_data_training"), bool):
        raise ValidationGateError("allow_real_data_training must be boolean")
    missing = [key for key in REQUIRED_PROVENANCE if not config.get(key)]
    if missing:
        raise ValidationGateError("missing mandatory build fields: " + ", ".join(missing))
    for key in REQUIRED_PROVENANCE:
        value = config[key]
        if isinstance(value, str) and not value.strip():
            raise ValidationGateError(f"{key} must be non-empty")
    if not isinstance(config["candidate_id"], str) or any(token in config["candidate_id"] for token in ("/", "\\", "..")):
        raise ValidationGateError("candidate_id must be a simple non-path identifier")
    for key in STRUCTURED_CONFIG_KEYS:
        if not isinstance(config[key], Mapping) and not (isinstance(config[key], str) and config[key].strip()):
            raise ValidationGateError(f"{key} must be a non-empty mapping or description")
    if not isinstance(config["output_root"], str) or not Path(config["output_root"]).is_absolute():
        raise ValidationGateError("output_root must be an explicit absolute path")
    if synthetic and config["allow_real_data_training"]:
        raise ValidationGateError("synthetic configuration cannot enable real-data training")
    if not synthetic:
        for key in ("licensing_evidence", "provenance_evidence", "grouping_approval"):
            value = config.get(key)
            if not isinstance(value, Mapping) or not value.get("source") or not value.get("date") or value.get("status") != "reviewed":
                raise ValidationGateError(f"real-data training requires reviewed {key} with source and date")
        if config.get("allow_real_data_training") is not True:
            raise ValidationGateError("real-data training is disabled unless explicitly enabled by reviewed configuration")


def refuse_real_data_training(config: Mapping[str, Any]) -> None:
    """Fail closed for this task and for unresolved real-data provenance."""

    validate_build_configuration(config, synthetic=False)
    raise ValidationGateError("real-data training is intentionally not implemented in the harness task")
