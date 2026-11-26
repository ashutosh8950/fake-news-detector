"""Duplicate-aware, non-training evaluation manifests and preflight checks.

This module deliberately does not import the production predictor, preprocessor,
serialized artifacts, or model-training code.  It only builds deterministic
row/group manifests from the two source CSV files and validates split feasibility.
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
import unicodedata
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Mapping, Sequence

RANDOM_STATE = 42  # Recorded metadata; the deterministic algorithm does not use randomness.
OUTPUT_ROOT = Path("evaluation_results") / "duplicate_aware" / "final_v5"
PRIMARY_POLICY = "all_keys_v1"
BODY_COMBINED_POLICY = "body_combined_only_v1"
LOW_INFORMATION_POLICY = "low_information_title_v1"
NORMALIZATION_POLICY_ID = "unicode_alphanumeric_v2"
NORMALIZATION_SPEC = "NFKC; casefold; every non-alphanumeric character to a separator; collapse separators to ASCII spaces; trim"
GROUPING_ALGORITHM_ID = "transitive_key_components_v1"
SPLIT_ALGORITHM_ID = "deterministic_group_split_v2"
MANIFEST_SCHEMA_VERSION = "duplicate_aware_manifest_v2"
RESERVATION_ALGORITHM_ID = "deterministic_reservation_certificate_v1"
LOW_INFORMATION_TITLES = (
    "na",
    "n/a",
    "no title",
    "none",
    "not available",
    "null",
    "title unavailable",
    "unknown",
    "untitled",
)

OBJECTIVE_SCALE = 10**12
MAX_CANDIDATE_EVALUATIONS = 1_000_000
MAX_EXACT_ORACLE_GROUPS = 250
MAX_ORACLE_STATES = 2_000_000

OUTER_TARGETS = {"test": 0.15, "train": 0.85}
INNER_TARGETS = {"proper_fit": 0.64, "method_selection": 0.16, "final_calibration": 0.20}


@dataclass(frozen=True)
class Row:
    row_id: str
    title: str
    body: str
    label: int
    source_file: str
    source_ordinal: int


@dataclass(frozen=True)
class Group:
    group_id: str
    member_ids: tuple[str, ...]
    keys: tuple[tuple[str, str], ...]
    class_counts: tuple[tuple[int, int], ...]

    @property
    def row_count(self) -> int:
        return len(self.member_ids)

    @property
    def class_count(self) -> dict[int, int]:
        return dict(self.class_counts)

    @property
    def classes(self) -> set[int]:
        return set(self.class_count)


@dataclass(frozen=True)
class Requirements:
    min_rows_by_class: Mapping[int, int]
    min_groups: int
    min_class_bearing_groups: Mapping[int, int]


@dataclass(frozen=True)
class FeasibilityResult:
    status: str
    reason: str
    states_explored: int = 0


class UnionFind:
    def __init__(self, members: Iterable[str]):
        members = tuple(members)
        self.parent = {member: member for member in members}
        self.rank = {member: 0 for member in members}

    def find(self, member: str) -> str:
        parent = self.parent[member]
        if parent != member:
            self.parent[member] = self.find(parent)
        return self.parent[member]

    def union(self, left: str, right: str) -> None:
        left_root = self.find(left)
        right_root = self.find(right)
        if left_root == right_root:
            return
        if self.rank[left_root] < self.rank[right_root]:
            left_root, right_root = right_root, left_root
        self.parent[right_root] = left_root
        if self.rank[left_root] == self.rank[right_root]:
            self.rank[left_root] += 1


def normalize_key(value: object) -> str:
    text = unicodedata.normalize("NFKC", "" if value is None else str(value))
    text = text.casefold()
    # isalnum() follows Python's Unicode character classification and, unlike
    # \w, does not treat underscore as an alphanumeric character.
    normalized = "".join(character if character.isalnum() else " " for character in text)
    return " ".join(normalized.split()).strip()


def _canonical_json(payload: object) -> bytes:
    return json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _source_metadata(path: Path, expected_label: int) -> dict[str, object]:
    source_bytes = path.read_bytes()
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        fieldnames = list(reader.fieldnames or [])
        row_count = sum(1 for _ in reader)
    required = {"title", "text"}
    missing = required - set(fieldnames)
    if missing:
        raise ValueError(f"{path} is missing columns: {sorted(missing)}")
    return {
        "filename": path.name,
        "sha256": _sha256_bytes(source_bytes),
        "size_bytes": len(source_bytes),
        "row_count": row_count,
        "schema_fingerprint": _sha256_bytes(_canonical_json({"columns": fieldnames})),
        "schema_columns": fieldnames,
        "label": expected_label,
    }


def _requirements_payload(requirements: Mapping[str, Requirements]) -> dict[str, object]:
    return {
        partition: {
            "min_rows_by_class": {str(label): int(value) for label, value in sorted(req.min_rows_by_class.items())},
            "min_groups": int(req.min_groups),
            "min_class_bearing_groups": {str(label): int(value) for label, value in sorted(req.min_class_bearing_groups.items())},
        }
        for partition, req in sorted(requirements.items())
    }


def _canonical_configuration(policy: str) -> dict[str, object]:
    if policy == PRIMARY_POLICY:
        selected_key_types = ["title", "body", "combined"]
    elif policy == BODY_COMBINED_POLICY:
        selected_key_types = ["body", "combined"]
    else:
        raise ValueError(f"Unknown grouping policy: {policy}")
    return {
        "policy_id": policy,
        "selected_key_types": selected_key_types,
        "normalization_policy_id": NORMALIZATION_POLICY_ID,
        "normalization_spec": NORMALIZATION_SPEC,
        "grouping_algorithm_id": GROUPING_ALGORITHM_ID,
        "split_algorithm_id": SPLIT_ALGORITHM_ID,
        "manifest_schema_version": MANIFEST_SCHEMA_VERSION,
        "reservation_algorithm_id": RESERVATION_ALGORITHM_ID,
        "feasibility_modes": ["exact_memoized_oracle", "reservation_certificate"],
        "random_state": RANDOM_STATE,
        "objective_scale": OBJECTIVE_SCALE,
        "max_candidate_evaluations": MAX_CANDIDATE_EVALUATIONS,
        "max_exact_oracle_groups": MAX_EXACT_ORACLE_GROUPS,
        "max_oracle_states": MAX_ORACLE_STATES,
        "outer_targets": OUTER_TARGETS,
        "inner_targets": INNER_TARGETS,
        "outer_requirements": _requirements_payload(outer_requirements()),
        "inner_requirements": _requirements_payload(inner_requirements()),
    }


def provenance_metadata(fake_path: Path, true_path: Path) -> dict[str, object]:
    configurations = {
        policy: _canonical_configuration(policy)
        for policy in (PRIMARY_POLICY, BODY_COMBINED_POLICY)
    }
    return {
        "provenance_schema_version": "manifest_provenance_v1",
        "inputs": {
            "fake": _source_metadata(fake_path, 0),
            "true": _source_metadata(true_path, 1),
        },
        "normalization_policy_id": NORMALIZATION_POLICY_ID,
        "normalization_spec": NORMALIZATION_SPEC,
        "grouping_algorithm_id": GROUPING_ALGORITHM_ID,
        "split_algorithm_id": SPLIT_ALGORITHM_ID,
        "reservation_algorithm_id": RESERVATION_ALGORITHM_ID,
        "manifest_schema_version": MANIFEST_SCHEMA_VERSION,
        "configurations": configurations,
        "configuration_fingerprints": {
            policy: _sha256_bytes(_canonical_json(configuration))
            for policy, configuration in configurations.items()
        },
    }


def source_rows(fake_path: Path, true_path: Path) -> list[Row]:
    rows: list[Row] = []
    for path, label, prefix in ((fake_path, 0, "fake"), (true_path, 1, "true")):
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            required = {"title", "text"}
            missing = required - set(reader.fieldnames or [])
            if missing:
                raise ValueError(f"{path} is missing columns: {sorted(missing)}")
            for ordinal, record in enumerate(reader):
                rows.append(
                    Row(
                        row_id=f"{prefix}:{ordinal}",
                        title=record.get("title") or "",
                        body=record.get("text") or "",
                        label=label,
                        source_file=path.name,
                        source_ordinal=ordinal,
                    )
                )
    return sorted(rows, key=lambda row: row.row_id)


def row_keys(row: Row) -> dict[str, str]:
    title = normalize_key(row.title)
    body = normalize_key(row.body)
    combined = normalize_key(f"{row.title} {row.body}")
    return {"title": title, "body": body, "combined": combined}


def _key_sets(rows: Sequence[Row], policy: str) -> dict[str, list[str]]:
    if policy == PRIMARY_POLICY:
        return {"title": ["title"], "body": ["body"], "combined": ["combined"]}
    if policy == BODY_COMBINED_POLICY:
        return {"body": ["body"], "combined": ["combined"]}
    raise ValueError(f"Unknown grouping policy: {policy}")


def build_groups(rows: Sequence[Row], policy: str = PRIMARY_POLICY) -> tuple[list[Group], dict[str, dict[str, str]]]:
    ordered_rows = sorted(rows, key=lambda row: row.row_id)
    uf = UnionFind(row.row_id for row in ordered_rows)
    keys_by_row = {row.row_id: row_keys(row) for row in ordered_rows}
    key_members: dict[tuple[str, str], list[str]] = defaultdict(list)
    selected_types = set(_key_sets(ordered_rows, policy))
    for row in ordered_rows:
        for key_type in sorted(selected_types):
            value = keys_by_row[row.row_id][key_type]
            if value:
                key_members[(key_type, value)].append(row.row_id)
    for key in sorted(key_members):
        members = sorted(key_members[key])
        for member in members[1:]:
            uf.union(members[0], member)

    components: dict[str, list[str]] = defaultdict(list)
    root_by_row = {}
    for row in ordered_rows:
        root = uf.find(row.row_id)
        root_by_row[row.row_id] = root
        components[root].append(row.row_id)
    component_keys: dict[str, set[tuple[str, str]]] = defaultdict(set)
    for key, members in key_members.items():
        for member in members:
            component_keys[root_by_row[member]].add(key)
    row_by_id = {row.row_id: row for row in ordered_rows}
    groups: list[Group] = []
    for member_ids in components.values():
        members = tuple(sorted(member_ids))
        keys = tuple(sorted(component_keys[uf.find(members[0])]))
        class_counts = Counter(row_by_id[row_id].label for row_id in members)
        group_id = "g_" + hashlib.sha256("\n".join(members).encode("utf-8")).hexdigest()
        groups.append(
            Group(
                group_id=group_id,
                member_ids=members,
                keys=keys,
                class_counts=tuple(sorted(class_counts.items())),
            )
        )
    return sorted(groups, key=lambda group: group.group_id), keys_by_row


def _q(value: float) -> int:
    return math.floor(value * OBJECTIVE_SCALE + 0.5)


def _class_totals(groups: Sequence[Group]) -> Counter:
    totals: Counter = Counter()
    for group in groups:
        totals.update(group.class_count)
    return totals


def _stats(groups: Sequence[Group], assignments: Mapping[str, str], partitions: Sequence[str]) -> dict[str, dict[str, object]]:
    result: dict[str, dict[str, object]] = {}
    for partition in partitions:
        selected = [group for group in groups if assignments.get(group.group_id) == partition]
        counts = Counter()
        class_groups = Counter()
        for group in selected:
            counts.update(group.class_count)
            for label in group.classes:
                class_groups[label] += 1
        result[partition] = {
            "rows": len([row_id for group in selected for row_id in group.member_ids]),
            "class_counts": {str(label): counts[label] for label in (0, 1)},
            "groups": len(selected),
            "class_bearing_groups": {str(label): class_groups[label] for label in (0, 1)},
        }
    return result


def _objective_key(groups: Sequence[Group], assignments: Mapping[str, str], targets: Mapping[str, float], partitions: Sequence[str], stats_override: Mapping[str, Mapping[str, object]] | None = None, include_assignment_tie: bool = True, totals_override: Mapping[int, int] | None = None) -> tuple:
    totals = totals_override if totals_override is not None else _class_totals(groups)
    total_rows = sum(totals.values())
    stats = stats_override if stats_override is not None else _stats(groups, assignments, partitions)
    row_dev = sum(
        targets[partition] * abs(stats[partition]["rows"] / total_rows - targets[partition])
        for partition in partitions
    )
    class0_dev = sum(
        targets[partition] * abs(stats[partition]["class_counts"]["0"] / totals[0] - targets[partition])
        for partition in partitions
    )
    class1_dev = sum(
        targets[partition] * abs(stats[partition]["class_counts"]["1"] / totals[1] - targets[partition])
        for partition in partitions
    )
    objective = 0.50 * row_dev + 0.25 * class0_dev + 0.25 * class1_dev
    class_dev = 0.5 * (class0_dev + class1_dev)
    assignment_tie = (
        tuple((group.group_id, assignments.get(group.group_id, "")) for group in sorted(groups, key=lambda item: item.group_id))
        if include_assignment_tie
        else ()
    )
    return (_q(objective), _q(row_dev), _q(class_dev), tuple(stats[p]["rows"] for p in partitions), assignment_tie)


def _objective_report(key: tuple) -> dict[str, object]:
    tie_text = json.dumps(key[4], ensure_ascii=True, separators=(",", ":"))
    return {
        "objective_quantized": int(key[0]),
        "row_deviation_quantized": int(key[1]),
        "class_deviation_quantized": int(key[2]),
        "partition_row_counts": [int(value) for value in key[3]],
        "assignment_tie_break_sha256": hashlib.sha256(tie_text.encode("utf-8")).hexdigest(),
        "assignment_tie_break_length": len(key[4]),
    }


def _clone_stats(stats: Mapping[str, Mapping[str, object]], partitions: Sequence[str]) -> dict[str, dict[str, object]]:
    return {
        partition: {
            "rows": int(stats[partition]["rows"]),
            "class_counts": dict(stats[partition]["class_counts"]),
            "groups": int(stats[partition]["groups"]),
            "class_bearing_groups": dict(stats[partition]["class_bearing_groups"]),
        }
        for partition in partitions
    }


def _add_group_to_stats(stats: dict[str, dict[str, object]], partition: str, group: Group) -> None:
    stats[partition]["rows"] += group.row_count
    stats[partition]["groups"] += 1
    for label, count in group.class_count.items():
        stats[partition]["class_counts"][str(label)] += count
        stats[partition]["class_bearing_groups"][str(label)] += 1


def _hard_requirements_ok(stats: Mapping[str, Mapping[str, object]], requirements: Mapping[str, Requirements]) -> bool:
    for partition, requirement in requirements.items():
        observed = stats[partition]
        if observed["groups"] < requirement.min_groups:
            return False
        for label, minimum in requirement.min_rows_by_class.items():
            if observed["class_counts"][str(label)] < minimum:
                return False
        for label, minimum in requirement.min_class_bearing_groups.items():
            if observed["class_bearing_groups"][str(label)] < minimum:
                return False
    return True


def _exact_feasible(groups: Sequence[Group], partitions: Sequence[str], requirements: Mapping[str, Requirements], fixed: Mapping[str, str]) -> FeasibilityResult:
    remaining = [group for group in sorted(groups, key=lambda item: item.group_id) if group.group_id not in fixed]
    state_count = 0
    memo: set[tuple[int, tuple[tuple[str, int, int, int], ...]]] = set()

    def recurse(index: int, assignment: dict[str, str]) -> bool:
        nonlocal state_count
        state_count += 1
        if state_count > MAX_ORACLE_STATES:
            raise RuntimeError("exact feasibility state limit reached")
        stats = _stats(groups, {**fixed, **assignment}, partitions)
        if index == len(remaining):
            return _hard_requirements_ok(stats, requirements)
        state = (
            index,
            tuple(
                (
                    p,
                    stats[p]["rows"],
                    stats[p]["class_counts"]["0"],
                    stats[p]["class_counts"]["1"],
                    stats[p]["groups"],
                    stats[p]["class_bearing_groups"]["0"],
                    stats[p]["class_bearing_groups"]["1"],
                )
                for p in partitions
            ),
        )
        if state in memo:
            return False
        group = remaining[index]
        for partition in partitions:
            assignment[group.group_id] = partition
            if recurse(index + 1, assignment):
                return True
            del assignment[group.group_id]
        memo.add(state)
        return False

    try:
        result = recurse(0, {})
    except RuntimeError as exc:
        return FeasibilityResult("not_established", str(exc), state_count)
    return FeasibilityResult("feasible" if result else "infeasible", "exact search", state_count)


def _constructive_feasible(groups: Sequence[Group], partitions: Sequence[str], requirements: Mapping[str, Requirements], fixed: Mapping[str, str]) -> FeasibilityResult:
    """Find a sufficient reservation for large inputs; failure is inconclusive."""
    assignment = dict(fixed)
    ordered = sorted((group for group in groups if group.group_id not in assignment), key=lambda item: (-item.row_count, item.group_id))
    for group in ordered:
        stats = _stats(groups, assignment, partitions)
        missing = []
        for partition in partitions:
            req = requirements[partition]
            observed = stats[partition]
            deficit = sum(max(0, req.min_rows_by_class[label] - observed["class_counts"][str(label)]) for label in (0, 1))
            deficit += max(0, req.min_groups - observed["groups"]) * 10
            deficit += sum(max(0, req.min_class_bearing_groups[label] - observed["class_bearing_groups"][str(label)]) * 10 for label in (0, 1))
            missing.append((deficit, partition))
        for _, partition in sorted(missing, key=lambda item: (-item[0], item[1])):
            candidate = {**assignment, group.group_id: partition}
            if _necessary_remaining_check(groups, candidate, partitions, requirements):
                assignment[group.group_id] = partition
                break
        else:
            return FeasibilityResult("not_established", "constructive reservation could not establish feasibility")
    stats = _stats(groups, assignment, partitions)
    if _hard_requirements_ok(stats, requirements):
        return FeasibilityResult("feasible", "constructive reservation")
    return FeasibilityResult("not_established", "constructive reservation did not satisfy all requirements")


def _necessary_remaining_check(groups: Sequence[Group], fixed: Mapping[str, str], partitions: Sequence[str], requirements: Mapping[str, Requirements]) -> bool:
    stats = _stats(groups, fixed, partitions)
    remaining = [group for group in groups if group.group_id not in fixed]
    remaining_rows = Counter()
    remaining_class_groups = Counter()
    for group in remaining:
        remaining_rows.update(group.class_count)
        for label in group.classes:
            remaining_class_groups[label] += 1
    for partition in partitions:
        req = requirements[partition]
        observed = stats[partition]
        for label, minimum in req.min_rows_by_class.items():
            if observed["class_counts"][str(label)] + remaining_rows[label] < minimum:
                return False
        if observed["groups"] + len(remaining) < req.min_groups:
            return False
        for label, minimum in req.min_class_bearing_groups.items():
            if observed["class_bearing_groups"][str(label)] + remaining_class_groups[label] < minimum:
                return False
    return True


def feasibility_oracle(groups: Sequence[Group], partitions: Sequence[str], requirements: Mapping[str, Requirements], fixed: Mapping[str, str] | None = None) -> FeasibilityResult:
    fixed = fixed or {}
    if not _necessary_remaining_check(groups, fixed, partitions, requirements):
        return FeasibilityResult("infeasible", "aggregate remaining counts cannot satisfy requirements")
    if len(groups) <= MAX_EXACT_ORACLE_GROUPS:
        return _exact_feasible(groups, partitions, requirements, fixed)
    return _constructive_feasible(groups, partitions, requirements, fixed)


def reservation_evidence_hash(evidence: Sequence[Mapping[str, object]]) -> str:
    canonical = sorted(evidence, key=lambda item: (int(item["selection_order"]), str(item["group_id"])))
    return _sha256_bytes(_canonical_json(canonical))


def validate_reservation_certificate(
    groups: Sequence[Group],
    partitions: Sequence[str],
    requirements: Mapping[str, Requirements],
    evidence: Sequence[Mapping[str, object]],
    final_assignments: Mapping[str, str],
    expected_hash: str,
    expected_reserved_group_count: int | None = None,
) -> None:
    """Independently validate serialized reservation evidence and its witness."""
    group_by_id = {group.group_id: group for group in groups}
    if reservation_evidence_hash(evidence) != expected_hash:
        raise AssertionError("reservation evidence hash mismatch")
    if expected_reserved_group_count is not None and len(evidence) != expected_reserved_group_count:
        raise AssertionError("reservation evidence count mismatch")
    if len({str(item.get("group_id")) for item in evidence}) != len(evidence):
        raise AssertionError("reservation evidence contains duplicate groups")
    reserved: dict[str, str] = {}
    for item in evidence:
        group_id = str(item.get("group_id"))
        partition = str(item.get("partition"))
        if group_id not in group_by_id:
            raise AssertionError(f"unknown reserved group: {group_id}")
        if partition not in partitions:
            raise AssertionError(f"unknown reserved partition: {partition}")
        group = group_by_id[group_id]
        expected_counts = {str(label): count for label, count in sorted(group.class_counts)}
        if item.get("row_count") != group.row_count or item.get("class_counts") != expected_counts:
            raise AssertionError(f"reserved group contribution mismatch: {group_id}")
        if item.get("classes") != sorted(group.classes):
            raise AssertionError(f"reserved group classes mismatch: {group_id}")
        if group_id not in final_assignments or final_assignments[group_id] != partition:
            raise AssertionError(f"final assignment does not match reservation: {group_id}")
        reserved[group_id] = partition

    if set(final_assignments) != set(group_by_id):
        raise AssertionError("final assignment does not cover exactly all groups")

    def independent_stats(assignments: Mapping[str, str]) -> dict[str, dict[str, object]]:
        result = {
            partition: {
                "rows": 0,
                "groups": 0,
                "class_counts": {"0": 0, "1": 0},
                "class_bearing_groups": {"0": 0, "1": 0},
            }
            for partition in partitions
        }
        for group_id, partition in assignments.items():
            if partition not in result:
                raise AssertionError(f"assignment uses unknown partition: {partition}")
            group = group_by_id[group_id]
            observed = result[partition]
            observed["rows"] += group.row_count
            observed["groups"] += 1
            for label, count in group.class_counts:
                observed["class_counts"][str(label)] += count
                observed["class_bearing_groups"][str(label)] += 1
        return result

    reservation_stats = independent_stats(reserved)
    for partition, requirement in requirements.items():
        observed = reservation_stats[partition]
        if observed["groups"] < requirement.min_groups:
            raise AssertionError(f"reservation misses group minimum: {partition}")
        for label, minimum in requirement.min_rows_by_class.items():
            if observed["class_counts"][str(label)] < minimum:
                raise AssertionError(f"reservation misses class-row minimum: {partition}/{label}")
        for label, minimum in requirement.min_class_bearing_groups.items():
            if observed["class_bearing_groups"][str(label)] < minimum:
                raise AssertionError(f"reservation misses class-bearing minimum: {partition}/{label}")

    final_stats = independent_stats(final_assignments)
    for partition, requirement in requirements.items():
        observed = final_stats[partition]
        if observed["groups"] < requirement.min_groups:
            raise AssertionError(f"final assignment misses group minimum: {partition}")
        for label, minimum in requirement.min_rows_by_class.items():
            if observed["class_counts"][str(label)] < minimum:
                raise AssertionError(f"final assignment misses class-row minimum: {partition}/{label}")
        for label, minimum in requirement.min_class_bearing_groups.items():
            if observed["class_bearing_groups"][str(label)] < minimum:
                raise AssertionError(f"final assignment misses class-bearing minimum: {partition}/{label}")


def _reservation_assignment(groups: Sequence[Group], partitions: Sequence[str], requirements: Mapping[str, Requirements]) -> tuple[dict[str, str], FeasibilityResult, list[dict[str, object]]]:
    """Reserve indivisible groups that certify every hard minimum.

    This is used for large inputs.  Once reserved, those groups are pinned to
    their reservation partition; assigning any remaining group cannot remove
    the certificate.  Failure is deliberately inconclusive rather than an
    assertion that no feasible assignment exists.
    """
    reserved: dict[str, str] = {}
    evidence: list[dict[str, object]] = []
    selection_order = 0
    ordered = sorted(groups, key=lambda item: (-item.row_count, item.group_id))
    for partition in partitions:
        while True:
            stats = _stats(groups, reserved, partitions)
            observed = stats[partition]
            req = requirements[partition]
            needs = (
                observed["groups"] < req.min_groups
                or any(observed["class_counts"][str(label)] < minimum for label, minimum in req.min_rows_by_class.items())
                or any(observed["class_bearing_groups"][str(label)] < minimum for label, minimum in req.min_class_bearing_groups.items())
            )
            if not needs:
                break
            candidates = []
            for group in ordered:
                if group.group_id in reserved:
                    continue
                score = 0
                group_counts = dict(group.class_counts)
                for label, minimum in req.min_rows_by_class.items():
                    score += min(max(0, minimum - observed["class_counts"][str(label)]), group_counts.get(label, 0))
                for label, minimum in req.min_class_bearing_groups.items():
                    if observed["class_bearing_groups"][str(label)] < minimum and label in group_counts:
                        score += 100
                if observed["groups"] < req.min_groups:
                    score += 100
                candidates.append((score, group.row_count, group.group_id, group))
            if not candidates:
                return reserved, FeasibilityResult("not_established", f"could not reserve requirements for partition {partition}"), evidence
            ranked = sorted(candidates, key=lambda item: (item[0], item[1], item[2]), reverse=True)
            selected_tuple = ranked[0]
            selected = selected_tuple[3]
            reserved[selected.group_id] = partition
            selection_order += 1
            evidence.append({
                "selection_order": selection_order,
                "partition": partition,
                "group_id": selected.group_id,
                "row_count": selected.row_count,
                "class_counts": {str(label): count for label, count in sorted(selected.class_counts)},
                "classes": sorted(selected.classes),
                "selection_score": selected_tuple[0],
                "candidate_rank": 1,
            })
    final_stats = _stats(groups, reserved, partitions)
    if not _hard_requirements_ok(final_stats, requirements):
        return reserved, FeasibilityResult("not_established", "reservation did not satisfy all hard requirements"), evidence
    return reserved, FeasibilityResult("feasible", "deterministic reservation certificate"), evidence


def _ordered_groups(groups: Sequence[Group]) -> list[Group]:
    return sorted(
        groups,
        key=lambda group: (
            -group.row_count,
            -max(group.class_count.values()),
            -abs(group.class_count.get(0, 0) - group.class_count.get(1, 0)),
            group.group_id,
        ),
    )


def split_groups(groups: Sequence[Group], targets: Mapping[str, float], requirements: Mapping[str, Requirements], max_candidate_evaluations: int = MAX_CANDIDATE_EVALUATIONS) -> tuple[dict[str, str], dict[str, object]]:
    partitions = tuple(targets)
    large_input = len(groups) > MAX_EXACT_ORACLE_GROUPS
    reservation: dict[str, str] = {}
    reservation_evidence: list[dict[str, object]] = []
    if large_input:
        reservation, initial, reservation_evidence = _reservation_assignment(groups, partitions, requirements)
    else:
        initial = feasibility_oracle(groups, partitions, requirements)
    if initial.status != "feasible":
        raise RuntimeError(f"split feasibility {initial.status}: {initial.reason}")
    assignments: dict[str, str] = {}
    totals = _class_totals(groups)
    running_stats = {partition: {"rows": 0, "class_counts": {"0": 0, "1": 0}, "groups": 0, "class_bearing_groups": {"0": 0, "1": 0}} for partition in partitions}
    candidate_evaluations = 0
    for group in _ordered_groups(groups):
        candidates = []
        allowed_partitions = (reservation[group.group_id],) if group.group_id in reservation else partitions
        for partition in allowed_partitions:
            trial = ({**assignments, group.group_id: partition} if not large_input else {})
            candidate_evaluations += 1
            if candidate_evaluations > max_candidate_evaluations:
                raise RuntimeError("candidate evaluation limit reached during initial assignment")
            result = FeasibilityResult("feasible", "pinned reservation") if large_input else feasibility_oracle(groups, partitions, requirements, trial)
            if result.status == "not_established":
                raise RuntimeError(f"split feasibility not_established: {result.reason}")
            if result.status == "feasible":
                candidate_stats = _clone_stats(running_stats, partitions)
                _add_group_to_stats(candidate_stats, partition, group)
                candidates.append((_objective_key(groups, trial, targets, partitions, candidate_stats, not large_input, totals), partition, candidate_stats))
        if not candidates:
            raise RuntimeError(f"no feasible assignment for group {group.group_id}")
        selected = min(candidates)
        assignments[group.group_id] = selected[1]
        running_stats = selected[2]

    accepted_changes = 0
    limit_reached = False
    if large_input:
        # The reservation certificate guarantees hard feasibility.  Avoid an
        # O(groups^2) local-swap scan for repository-scale manifests.
        limit_reached = False
        final_stats = _stats(groups, assignments, partitions)
        if not _hard_requirements_ok(final_stats, requirements):
            raise RuntimeError("final split failed hard feasibility validation")
        reservation_hash = reservation_evidence_hash(reservation_evidence)
        validate_reservation_certificate(groups, partitions, requirements, reservation_evidence, assignments, reservation_hash, len(reservation))
        return assignments, {
            "candidate_evaluations": candidate_evaluations,
            "accepted_changes": accepted_changes,
            "optimization_limit_reached": False,
            "objective_key": _objective_report(_objective_key(groups, assignments, targets, partitions)),
            "statistics": final_stats,
            "feasibility_mode": "reservation_certificate",
            "reservation_algorithm_id": RESERVATION_ALGORITHM_ID,
            "reserved_group_count": len(reservation),
            "reservation_evidence": reservation_evidence,
            "reservation_hash": reservation_hash,
            "optimization_note": "Large-input path uses reservation-pinned deterministic greedy assignment; exhaustive local swaps are not attempted.",
        }

    while True:
        current_key = _objective_key(groups, assignments, targets, partitions)
        best: tuple[tuple, dict[str, str]] | None = None
        ordered_ids = [group.group_id for group in sorted(groups, key=lambda item: item.group_id)]
        for group_id in ordered_ids:
            if group_id in reservation:
                continue
            current_partition = assignments[group_id]
            for partition in partitions:
                if partition == current_partition:
                    continue
                candidate_evaluations += 1
                if candidate_evaluations > max_candidate_evaluations:
                    limit_reached = True
                    break
                trial = dict(assignments)
                trial[group_id] = partition
                result = FeasibilityResult("feasible", "pinned reservation") if large_input else feasibility_oracle(groups, partitions, requirements, trial)
                if result.status == "not_established":
                    raise RuntimeError(f"split feasibility not_established: {result.reason}")
                if result.status != "feasible":
                    continue
                key = _objective_key(groups, trial, targets, partitions)
                if key < current_key and (best is None or key < best[0]):
                    best = (key, trial)
            if limit_reached:
                break
        if limit_reached:
            break
        for left_index, left_id in enumerate(ordered_ids):
            for right_id in ordered_ids[left_index + 1 :]:
                if assignments[left_id] == assignments[right_id]:
                    continue
                if left_id in reservation or right_id in reservation:
                    continue
                candidate_evaluations += 1
                if candidate_evaluations > max_candidate_evaluations:
                    limit_reached = True
                    break
                trial = dict(assignments)
                trial[left_id], trial[right_id] = trial[right_id], trial[left_id]
                result = FeasibilityResult("feasible", "pinned reservation") if large_input else feasibility_oracle(groups, partitions, requirements, trial)
                if result.status == "not_established":
                    raise RuntimeError(f"split feasibility not_established: {result.reason}")
                if result.status != "feasible":
                    continue
                key = _objective_key(groups, trial, targets, partitions)
                if key < current_key and (best is None or key < best[0]):
                    best = (key, trial)
            if limit_reached:
                break
        if limit_reached or best is None:
            break
        assignments = best[1]
        accepted_changes += 1

    final_stats = _stats(groups, assignments, partitions)
    if not _hard_requirements_ok(final_stats, requirements):
        raise RuntimeError("final split failed hard feasibility validation")
    return assignments, {
        "candidate_evaluations": candidate_evaluations,
        "accepted_changes": accepted_changes,
        "optimization_limit_reached": limit_reached,
        "objective_key": _objective_report(_objective_key(groups, assignments, targets, partitions)),
        "statistics": final_stats,
        "feasibility_mode": "reservation_certificate" if large_input else "exact_memoized_oracle",
        "reservation_algorithm_id": RESERVATION_ALGORITHM_ID if large_input else None,
        "reserved_group_count": len(reservation),
        "reservation_evidence": reservation_evidence,
        "reservation_hash": reservation_evidence_hash(reservation_evidence),
    }


def outer_requirements() -> dict[str, Requirements]:
    return {
        "test": Requirements({0: 50, 1: 50}, 2, {0: 2, 1: 2}),
        "train": Requirements({0: 50, 1: 50}, 2, {0: 2, 1: 2}),
    }


def inner_requirements() -> dict[str, Requirements]:
    return {
        "proper_fit": Requirements({0: 50, 1: 50}, 2, {0: 2, 1: 2}),
        "method_selection": Requirements({0: 30, 1: 30}, 2, {0: 2, 1: 2}),
        "final_calibration": Requirements({0: 30, 1: 30}, 2, {0: 2, 1: 2}),
    }


def low_information_diagnostic(rows: Sequence[Row], groups: Sequence[Group], keys_by_row: Mapping[str, Mapping[str, str]]) -> dict[str, object]:
    normalized_placeholders = set(LOW_INFORMATION_TITLES)
    affected_rows = {row.row_id for row in rows if keys_by_row[row.row_id]["title"] in normalized_placeholders}
    original_membership = {row_id: group.group_id for group in groups for row_id in group.member_ids}
    filtered_groups: list[Group] = []
    # Rebuild with all keys except placeholder title edges, retaining every row.
    uf = UnionFind(row.row_id for row in rows)
    key_members: dict[tuple[str, str], list[str]] = defaultdict(list)
    for row in rows:
        for key_type in ("body", "combined"):
            value = keys_by_row[row.row_id][key_type]
            if value:
                key_members[(key_type, value)].append(row.row_id)
        title = keys_by_row[row.row_id]["title"]
        if title and title not in normalized_placeholders:
            key_members[("title", title)].append(row.row_id)
    for key in sorted(key_members):
        members = sorted(key_members[key])
        for member in members[1:]:
            uf.union(members[0], member)
    row_by_id = {row.row_id: row for row in rows}
    components: dict[str, list[str]] = defaultdict(list)
    root_by_row = {}
    for row in sorted(rows, key=lambda item: item.row_id):
        root = uf.find(row.row_id)
        root_by_row[row.row_id] = root
        components[root].append(row.row_id)
    component_keys: dict[str, set[tuple[str, str]]] = defaultdict(set)
    for key, members in key_members.items():
        for member in members:
            component_keys[root_by_row[member]].add(key)
    for members in components.values():
        members_tuple = tuple(sorted(members))
        key_tuple = tuple(sorted(component_keys[uf.find(members_tuple[0])]))
        counts = Counter(row_by_id[row_id].label for row_id in members_tuple)
        group_id = "g_" + hashlib.sha256("\n".join(members_tuple).encode("utf-8")).hexdigest()
        filtered_groups.append(Group(group_id, members_tuple, key_tuple, tuple(sorted(counts.items()))))
    filtered_membership = {row_id: group.group_id for group in filtered_groups for row_id in group.member_ids}
    unchanged_incident = sorted(row_id for row_id in affected_rows if original_membership[row_id] == filtered_membership[row_id])
    split_components = []
    still_connected = []
    for group in groups:
        new_groups = sorted({filtered_membership[row_id] for row_id in group.member_ids})
        if len(new_groups) > 1:
            split_components.append({"original_group_id": group.group_id, "new_group_ids": new_groups, "row_count": group.row_count})
        elif any(key_type == "title" and key in normalized_placeholders for key_type, key in group.keys):
            still_connected.append({"group_id": group.group_id, "row_count": group.row_count, "new_group_id": new_groups[0]})
    return {
        "policy_id": LOW_INFORMATION_POLICY,
        "normalization": NORMALIZATION_SPEC,
        "placeholder_titles": sorted(normalized_placeholders),
        "incident_row_count": len(affected_rows),
        "incident_rows_membership_unchanged": unchanged_incident,
        "groups_split": sorted(split_components, key=lambda item: (item["original_group_id"], item["new_group_ids"])),
        "groups_still_connected_through_other_keys": sorted(still_connected, key=lambda item: item["group_id"]),
        "filtered_group_count": len(filtered_groups),
    }


def validate_manifest(rows: Sequence[Row], groups: Sequence[Group], assignments: Mapping[str, str], keys_by_row: Mapping[str, Mapping[str, str]], partitions: Sequence[str], key_types: Sequence[str] = ("title", "body", "combined")) -> None:
    row_ids = {row.row_id for row in rows}
    assigned_ids = [row_id for group in groups for row_id in group.member_ids]
    if len(assigned_ids) != len(set(assigned_ids)) or set(assigned_ids) != row_ids:
        raise AssertionError("manifest does not assign every row exactly once")
    if set(assignments) != {group.group_id for group in groups}:
        raise AssertionError("manifest does not assign every group exactly once")
    for key_type in key_types:
        owners: dict[str, str] = {}
        for group in groups:
            partition = assignments[group.group_id]
            for row_id in group.member_ids:
                value = keys_by_row[row_id][key_type]
                if value and value in owners and owners[value] != partition:
                    raise AssertionError(f"{key_type} key crosses partitions: {value}")
                if value:
                    owners[value] = partition
    if any(partition not in partitions for partition in assignments.values()):
        raise AssertionError("unknown partition in manifest")


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8", newline="\n") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write("\n")


def write_manifest(path: Path, rows: Sequence[Row], groups: Sequence[Group], assignments: Mapping[str, str], keys_by_row: Mapping[str, Mapping[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    row_to_group = {row_id: group.group_id for group in groups for row_id in group.member_ids}
    with path.open("x", encoding="utf-8", newline="\n") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(["row_id", "source_file", "source_ordinal", "label", "group_id", "partition"])
        for row in sorted(rows, key=lambda item: item.row_id):
            group_id = row_to_group[row.row_id]
            writer.writerow([row.row_id, row.source_file, row.source_ordinal, row.label, group_id, assignments[group_id]])


def run_manifest_preflight(fake_path: Path = Path("data/Fake.csv"), true_path: Path = Path("data/True.csv"), output_root: Path = OUTPUT_ROOT) -> dict[str, object]:
    rows = source_rows(fake_path, true_path)
    provenance = provenance_metadata(fake_path, true_path)
    if output_root.exists():
        raise FileExistsError(f"Refusing to use existing output namespace: {output_root}")
    policies = ((PRIMARY_POLICY, OUTER_TARGETS), (BODY_COMBINED_POLICY, OUTER_TARGETS))
    target_files = []
    for policy, _ in policies:
        directory = output_root / ("primary" if policy == PRIMARY_POLICY else "body_combined_only")
        target_files.extend([directory / "split_manifest.csv", directory / "inner_split_manifest.csv", directory / "group_summary.json", directory / "preflight_report.json"])
    target_files.append(output_root / "low_information_title_v1" / "diagnostic_report.json")
    conflicts = [str(path) for path in target_files if path.exists()]
    if conflicts:
        raise FileExistsError("Refusing to overwrite existing targets: " + ", ".join(conflicts))

    result: dict[str, object] = {
        "random_state": RANDOM_STATE,
        "normalization": NORMALIZATION_SPEC,
        "normalization_policy_id": NORMALIZATION_POLICY_ID,
        "provenance": provenance,
        "policies": {},
    }
    for policy, targets in policies:
        groups, keys = build_groups(rows, policy)
        assignments, split_info = split_groups(groups, targets, outer_requirements())
        policy_configuration = provenance["configurations"][policy]
        policy_configuration_fingerprint = provenance["configuration_fingerprints"][policy]
        grouping_keys = ("title", "body", "combined") if policy == PRIMARY_POLICY else ("body", "combined")
        validate_manifest(rows, groups, assignments, keys, tuple(targets), grouping_keys)
        outer_train_ids = {group.group_id for group in groups if assignments[group.group_id] == "train"}
        inner_groups = [group for group in groups if group.group_id in outer_train_ids]
        inner_row_ids = {row_id for group in inner_groups for row_id in group.member_ids}
        inner_rows = [row for row in rows if row.row_id in inner_row_ids]
        inner_assignments, inner_info = split_groups(inner_groups, INNER_TARGETS, inner_requirements())
        validate_manifest(inner_rows, inner_groups, inner_assignments, keys, tuple(INNER_TARGETS), grouping_keys)
        directory = output_root / ("primary" if policy == PRIMARY_POLICY else "body_combined_only")
        write_manifest(directory / "split_manifest.csv", rows, groups, assignments, keys)
        write_manifest(directory / "inner_split_manifest.csv", inner_rows, inner_groups, inner_assignments, keys)
        write_json(directory / "group_summary.json", {
            "policy": policy,
            "configuration": policy_configuration,
            "configuration_fingerprint": policy_configuration_fingerprint,
            "normalization_policy_id": NORMALIZATION_POLICY_ID,
            "grouping_algorithm_id": GROUPING_ALGORITHM_ID,
            "manifest_schema_version": MANIFEST_SCHEMA_VERSION,
            "provenance": provenance,
            "group_count": len(groups),
            "largest_groups": [
                {
                    "group_id": group.group_id,
                    "row_count": group.row_count,
                    "class_counts": dict(group.class_counts),
                    "keys": [
                        {"key_type": key_type, "key_sha256": hashlib.sha256(key_value.encode("utf-8")).hexdigest()}
                        for key_type, key_value in group.keys
                    ],
                }
                for group in sorted(groups, key=lambda item: (-item.row_count, item.group_id))[:20]
            ],
            "inner_split": inner_info,
        })
        write_json(directory / "preflight_report.json", {
            "policy": policy,
            "configuration": policy_configuration,
            "configuration_fingerprint": policy_configuration_fingerprint,
            "normalization": NORMALIZATION_SPEC,
            "normalization_policy_id": NORMALIZATION_POLICY_ID,
            "grouping_algorithm_id": GROUPING_ALGORITHM_ID,
            "split_algorithm_id": SPLIT_ALGORITHM_ID,
            "manifest_schema_version": MANIFEST_SCHEMA_VERSION,
            "provenance": provenance,
            "outer_split": split_info,
            "inner_split": inner_info,
            "row_count": len(rows),
            "group_count": len(groups),
            "training_and_calibration_only": True,
        })
        result["policies"][policy] = {
            "rows": len(rows),
            "groups": len(groups),
            "configuration_fingerprint": policy_configuration_fingerprint,
            "outer": split_info,
            "inner": inner_info,
        }

    primary_groups, primary_keys = build_groups(rows, PRIMARY_POLICY)
    diagnostic = low_information_diagnostic(rows, primary_groups, primary_keys)
    diagnostic["provenance"] = provenance
    diagnostic["grouping_algorithm_id"] = GROUPING_ALGORITHM_ID
    diagnostic["manifest_schema_version"] = MANIFEST_SCHEMA_VERSION
    write_json(output_root / "low_information_title_v1" / "diagnostic_report.json", diagnostic)
    result["low_information_diagnostic"] = diagnostic
    return result


if __name__ == "__main__":
    summary = run_manifest_preflight()
    print(json.dumps(summary, indent=2, sort_keys=True))
