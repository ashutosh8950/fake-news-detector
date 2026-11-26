import hashlib
import json
from pathlib import Path

import pytest

from duplicate_aware_manifest import (
    BODY_COMBINED_POLICY,
    INNER_TARGETS,
    PRIMARY_POLICY,
    Group,
    Requirements,
    Row,
    build_groups,
    feasibility_oracle,
    low_information_diagnostic,
    normalize_key,
    outer_requirements,
    provenance_metadata,
    reservation_evidence_hash,
    row_keys,
    run_manifest_preflight,
    split_groups,
    validate_manifest,
    validate_reservation_certificate,
    write_json,
)


def rows_for_tests():
    return [
        Row("fake:0", "No Title", "Same body", 0, "Fake.csv", 0),
        Row("fake:1", "Bridge", "Different", 0, "Fake.csv", 1),
        Row("true:0", "bridge", "Other", 1, "True.csv", 0),
        Row("true:1", "Real", "Same body", 1, "True.csv", 1),
        Row("true:2", "Unique", "Unique body", 1, "True.csv", 2),
        Row("fake:2", "Fake", "Fake body", 0, "Fake.csv", 2),
    ]


def test_normalization_behavior():
    assert normalize_key("  HéLLo—world\n") == "héllo world"
    assert normalize_key(None) == ""


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("A_B", "a b"),
        ("A__B!!!C", "a b c"),
        ("---Leading and trailing---", "leading and trailing"),
        ("tabs\tand\nnewlines", "tabs and newlines"),
        ("   \t\n", ""),
        ("Καλημέρα ١٢٣", "καλημέρα ١٢٣"),
        ("Ａ＿Ｂ", "a b"),
        ("Straße", "strasse"),
        ("!!!___···", ""),
    ],
)
def test_normalization_contract_regressions(raw, expected):
    assert normalize_key(raw) == expected


def test_grouping_keys_and_diagnostic_use_normalization_contract():
    row = Row("fake:0", "A_B", "C__D", 0, "Fake.csv", 0)
    assert row_keys(row) == {"title": "a b", "body": "c d", "combined": "a b c d"}


def test_provenance_fingerprints_are_exact_and_configuration_sensitive(tmp_path: Path):
    fake = tmp_path / "Fake.csv"
    true = tmp_path / "True.csv"
    fake_bytes = b"title,text\nA_B,Body\n"
    true_bytes = b"title,text\nReal,Truth\n"
    fake.write_bytes(fake_bytes)
    true.write_bytes(true_bytes)
    metadata = provenance_metadata(fake, true)
    assert metadata["inputs"]["fake"]["sha256"] == hashlib.sha256(fake_bytes).hexdigest()
    assert metadata["inputs"]["fake"]["size_bytes"] == len(fake_bytes)
    assert metadata["inputs"]["fake"]["row_count"] == 1
    assert metadata["inputs"]["fake"]["schema_columns"] == ["title", "text"]
    assert metadata["configuration_fingerprints"][PRIMARY_POLICY] != metadata["configuration_fingerprints"][BODY_COMBINED_POLICY]
    assert metadata["configurations"][PRIMARY_POLICY]["selected_key_types"] != metadata["configurations"][BODY_COMBINED_POLICY]["selected_key_types"]
    fake.write_bytes(fake_bytes + b"\n")
    changed = provenance_metadata(fake, true)
    assert changed["inputs"]["fake"]["sha256"] != metadata["inputs"]["fake"]["sha256"]
    assert changed["configuration_fingerprints"] == metadata["configuration_fingerprints"]


def test_configuration_fingerprints_are_policy_and_constraint_sensitive():
    from duplicate_aware_manifest import _canonical_configuration, _canonical_json, _sha256_bytes

    primary = _canonical_configuration(PRIMARY_POLICY)
    sensitivity = _canonical_configuration(BODY_COMBINED_POLICY)
    assert _sha256_bytes(_canonical_json(primary)) != _sha256_bytes(_canonical_json(sensitivity))
    changed = dict(primary)
    changed["outer_targets"] = {"test": 0.20, "train": 0.80}
    assert _sha256_bytes(_canonical_json(primary)) != _sha256_bytes(_canonical_json(changed))
    assert _sha256_bytes(_canonical_json(primary)) == _sha256_bytes(_canonical_json(dict(primary)))


def test_reservation_certificate_validation_and_hash_sensitivity():
    groups = [
        Group("g0", ("fake:0", "true:0"), (("body", "a"),), ((0, 1), (1, 1))),
        Group("g1", ("fake:1", "true:1"), (("body", "b"),), ((0, 1), (1, 1))),
    ]
    requirements = {
        "left": Requirements({0: 1, 1: 1}, 1, {0: 1, 1: 1}),
        "right": Requirements({0: 1, 1: 1}, 1, {0: 1, 1: 1}),
    }
    evidence = [
        {"selection_order": 1, "partition": "left", "group_id": "g0", "row_count": 2, "class_counts": {"0": 1, "1": 1}, "classes": [0, 1], "selection_score": 1, "candidate_rank": 1},
        {"selection_order": 2, "partition": "right", "group_id": "g1", "row_count": 2, "class_counts": {"0": 1, "1": 1}, "classes": [0, 1], "selection_score": 1, "candidate_rank": 1},
    ]
    assignments = {"g0": "left", "g1": "right"}
    digest = reservation_evidence_hash(evidence)
    with pytest.raises(AssertionError):
        validate_reservation_certificate(groups, ("left", "right"), requirements, evidence, assignments, "bad")
    with pytest.raises(AssertionError):
        validate_reservation_certificate(groups, ("left", "right"), requirements, evidence + [dict(evidence[0])], assignments, reservation_evidence_hash(evidence + [dict(evidence[0])]))
    with pytest.raises(AssertionError):
        validate_reservation_certificate(groups, ("left", "right"), requirements, evidence[:1], assignments, reservation_evidence_hash(evidence[:1]), 2)
    with pytest.raises(AssertionError):
        validate_reservation_certificate(groups, ("left", "right"), requirements, [{**evidence[0], "group_id": "unknown"}, evidence[1]], assignments, reservation_evidence_hash([{**evidence[0], "group_id": "unknown"}, evidence[1]]))
    validate_reservation_certificate(groups, ("left", "right"), requirements, evidence, assignments, digest)
    changed = [dict(item) for item in evidence]
    changed[0]["partition"] = "right"
    assert reservation_evidence_hash(changed) != digest


def test_output_namespace_is_exclusive(tmp_path: Path):
    occupied = tmp_path / "already_exists"
    occupied.mkdir()
    fake = tmp_path / "Fake.csv"
    true = tmp_path / "True.csv"
    fake.write_text("title,text\nA,B\n", encoding="utf-8", newline="")
    true.write_text("title,text\nC,D\n", encoding="utf-8", newline="")
    with pytest.raises(FileExistsError, match="existing output namespace"):
        run_manifest_preflight(fake, true, occupied)


def test_transitive_grouping_and_conflict_preservation():
    groups, keys = build_groups(rows_for_tests(), PRIMARY_POLICY)
    memberships = {row_id: group.group_id for group in groups for row_id in group.member_ids}
    assert memberships["fake:0"] == memberships["true:1"]
    assert memberships["fake:1"] == memberships["true:0"]
    conflict = [group for group in groups if set(dict(group.class_counts)) == {0, 1}]
    assert conflict
    assert all(group.row_count >= 2 for group in conflict)


def test_mixed_label_group_counts_for_feasibility():
    groups, _ = build_groups(rows_for_tests(), PRIMARY_POLICY)
    mixed = next(group for group in groups if set(dict(group.class_counts)) == {0, 1})
    assert mixed.classes == {0, 1}
    result = feasibility_oracle(groups, ("test", "train"), outer_requirements())
    assert result.status in {"feasible", "infeasible", "not_established"}


def test_infeasible_and_not_established_outcomes(monkeypatch):
    rows = [Row("fake:0", "a", "b", 0, "Fake.csv", 0), Row("true:0", "c", "d", 1, "True.csv", 0)]
    groups, _ = build_groups(rows)
    impossible = {"test": Requirements({0: 2, 1: 2}, 1, {0: 1, 1: 1}), "train": Requirements({0: 2, 1: 2}, 1, {0: 1, 1: 1})}
    assert feasibility_oracle(groups, ("test", "train"), impossible).status == "infeasible"
    monkeypatch.setattr("duplicate_aware_manifest.MAX_EXACT_ORACLE_GROUPS", 0)
    monkeypatch.setattr("duplicate_aware_manifest._necessary_remaining_check", lambda *args, **kwargs: True)
    monkeypatch.setattr("duplicate_aware_manifest._constructive_feasible", lambda *args, **kwargs: type("R", (), {"status": "not_established", "reason": "test limit", "states_explored": 0})())
    result = feasibility_oracle(groups, ("test", "train"), outer_requirements())
    assert result.status == "not_established"


def test_outer_and_inner_partition_integrity(monkeypatch):
    rows = [
        Row(f"fake:{index}", f"fake title {index}", f"fake body {index}", 0, "Fake.csv", index)
        for index in range(12)
    ] + [
        Row(f"true:{index}", f"true title {index}", f"true body {index}", 1, "True.csv", index)
        for index in range(12)
    ]
    groups, keys = build_groups(rows, PRIMARY_POLICY)
    outer_requirements_small = {
        "test": Requirements({0: 2, 1: 2}, 2, {0: 2, 1: 2}),
        "train": Requirements({0: 2, 1: 2}, 2, {0: 2, 1: 2}),
    }
    inner_requirements_small = {
        "proper_fit": Requirements({0: 2, 1: 2}, 2, {0: 2, 1: 2}),
        "method_selection": Requirements({0: 1, 1: 1}, 2, {0: 2, 1: 2}),
        "final_calibration": Requirements({0: 1, 1: 1}, 2, {0: 2, 1: 2}),
    }
    outer, _ = split_groups(groups, {"test": 0.15, "train": 0.85}, outer_requirements_small, max_candidate_evaluations=2_000)
    inner, _ = split_groups(groups, INNER_TARGETS, inner_requirements_small, max_candidate_evaluations=2_000)
    validate_manifest(rows, groups, outer, keys, ("test", "train"))
    validate_manifest(rows, groups, inner, keys, tuple(INNER_TARGETS))


def test_low_information_diagnostic_classification():
    rows = rows_for_tests()
    groups, keys = build_groups(rows, PRIMARY_POLICY)
    diagnostic = low_information_diagnostic(rows, groups, keys)
    assert diagnostic["policy_id"] == "low_information_title_v1"
    assert diagnostic["normalization"]
    assert diagnostic["incident_row_count"] >= 1
    assert "groups_split" in diagnostic
    assert "groups_still_connected_through_other_keys" in diagnostic


def test_repeated_permutations_have_identical_groups_and_keys():
    rows = rows_for_tests()
    baseline = build_groups(rows, PRIMARY_POLICY)
    permutations = [list(reversed(rows)), [rows[index] for index in (2, 0, 5, 1, 4, 3)]]
    for permutation in permutations:
        assert build_groups(permutation, PRIMARY_POLICY) == baseline
        assert build_groups(permutation, BODY_COMBINED_POLICY) == build_groups(rows, BODY_COMBINED_POLICY)


def test_serialization_stability(tmp_path: Path):
    payload = {"b": 2, "a": ["x", "y"]}
    first = tmp_path / "one.json"
    second = tmp_path / "two.json"
    write_json(first, payload)
    write_json(second, payload)
    assert first.read_bytes() == second.read_bytes()
    assert json.loads(first.read_text(encoding="utf-8")) == payload
