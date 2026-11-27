# Task 23 — Harness Hardening and Adversarial Validation Report

**Date:** 2026-10-22  
**Result:** **PASS WITH ONE ENVIRONMENT-DEPENDENT TEST SKIPPED**  
**Scope:** Static review and synthetic fixtures only. No real-data training or model-artifact operation occurred.

## Executive verdict

The Task 22 harness passed the adversarial review after hardening. The final synthetic suite completed with **15 passed and 1 skipped**. The skipped test attempted a directory symlink alias; Windows returned `WinError 1314` because symlink creation privilege was unavailable. The harness itself resolves paths before validation, but that specific filesystem-alias case was not executable in this environment.

This result demonstrates harness behavior on synthetic inputs only. It does not resolve dataset provenance, licensing, grouping-policy approval, environment locking, release authentication, or production readiness.

## Findings from implementation review

### Defects found and fixed

1. **Caller-selected namespace could escape the intended repository namespace.** `allowed_namespace` was accepted without requiring it to remain under the new candidate harness directory. It now must resolve inside `evaluation_results/new_release_candidate_2026-10-22/harness/`.
2. **Existing empty output directories were previously accepted.** The harness could validate an empty existing root and fail later at `mkdir`. It now rejects every existing output root before creation, preventing accidental reuse or overwrite.
3. **Configuration validation was permissive.** Missing values were checked, but unexpected fields, non-boolean flags, path-like candidate IDs, non-absolute output roots, and contradictory synthetic/real-data settings were not fully rejected. These checks are now fail-closed.
4. **The configured output root was not bound to the validated output root.** `record_output_plan()` now requires the absolute configured path to resolve exactly to the already validated path.
5. **Mixed-label groups were only reported.** They are now rejected unless `allow_mixed_label_groups=True` is explicitly supplied. When explicitly allowed, the report retains the mixed-group list and class-coverage checks remain active.
6. **A plan-write failure could leave a newly created candidate directory.** The plan writer now performs best-effort cleanup of the directory it created after a simulated write failure. This is explicitly not claimed to defend against filesystem races.

### Existing protections confirmed by review

- Path resolution uses `Path.resolve(strict=False)`, so `..` traversal and existing symlink components are resolved before containment checks.
- Output roots must be within the designated new namespace and outside production/shared roots.
- Required labels are restricted to integer 0 and 1; booleans are rejected.
- Group IDs must be non-empty strings.
- Partition assignments are checked after creation for empty partitions, required class coverage, and pairwise group overlap.
- Seed, target fractions, group IDs by partition, counts, mixed-label groups, and the non-optimal algorithm identifier are recorded in the split report.
- Real-data training remains refused, and a configuration flag cannot bypass reviewed licensing/provenance checks.

The implementation does **not** claim immunity to a concurrent filesystem race between validation and creation. The report and code document cleanup as best effort only.

## Changes made

Only files within the Task 22 harness directory were changed or added:

- `evaluation_results/new_release_candidate_2026-10-22/harness/isolated_build_harness.py`
  - constrained allowed namespaces;
  - rejected all existing roots;
  - added strict configuration type/value/contradiction checks;
  - bound configuration `output_root` to the validated path;
  - added explicit mixed-label policy;
  - added partial-plan cleanup.
- `evaluation_results/new_release_candidate_2026-10-22/harness/tests/test_isolated_build_harness.py`
  - added adversarial path, configuration, mixed-label, and cleanup tests;
  - updated synthetic plan fixtures to use explicit absolute roots.
- `evaluation_results/new_release_candidate_2026-10-22/harness/TASK23_HARNESS_HARDENING_REPORT.md`

The Task 22 template, Task 22 report, production code, existing evaluation directories, and prior audit reports were not modified.

## Adversarial synthetic test results

Command executed:

```text
.venv\Scripts\python.exe -m pytest evaluation_results/new_release_candidate_2026-10-22/harness/tests/test_isolated_build_harness.py -q -rs
```

Result:

```text
15 passed, 1 skipped in 0.19s
```

Passed coverage includes:

- same-group rows remaining in one partition;
- deterministic assignments for identical inputs and seed;
- missing, empty, and invalid group IDs;
- invalid labels and insufficient groups;
- explicit mixed-label rejection and opt-in reporting;
- production/shared path rejection;
- `..` traversal and external namespace rejection;
- path-alias containment behavior;
- existing-root overwrite rejection;
- unresolved real-data provenance refusal;
- contradictory, unexpected, and invalid configuration values;
- absolute output-root enforcement and exact path binding;
- no artifacts after failed validation;
- simulated plan-write cleanup;
- mutually disjoint train/selection/calibration/test groups; and
- planned paths recorded before future training.

Skipped test:

- Directory symlink alias test. Windows returned `WinError 1314` (“A required privilege is not held by the client”). It was skipped with an explicit reason; no privilege escalation or alternate filesystem was used.

No repository-wide tests were run because this task required synthetic-only testing and broad application tests could exercise production loading paths.

## Existing duplicate-aware grouping evidence

The existing `duplicate_aware_manifest.py` was inspected read-only. Its declared policies are:

- `all_keys_v1`: title, body, and combined-text keys;
- `body_combined_only_v1`: body and combined-text keys; and
- `low_information_title_v1`: a diagnostic policy for placeholder/low-information titles.

The implementation records normalization `NFKC; casefold; non-alphanumeric runs to spaces; collapse whitespace; trim`, grouping algorithm `transitive_key_components_v1`, split algorithm `deterministic_group_split_v2`, manifest schema `duplicate_aware_manifest_v2`, and reservation/feasibility metadata. It also has code to calculate source file hashes, sizes, row counts, and schema fingerprints.

The inspected existing reports show:

| Existing manifest | Policy | Rows | Groups | Outer partitions | Inner partitions |
|---|---|---:|---:|---|---|
| `evaluation_results/duplicate_aware/final/primary/` | `all_keys_v1` | 24,353 | 24,053 | train/test | proper_fit/method_selection/final_calibration |
| `evaluation_results/duplicate_aware/final/body_combined_only/` | `body_combined_only_v1` | 24,353 | 24,349 | train/test | proper_fit/method_selection/final_calibration |
| `evaluation_results/duplicate_aware/final/low_information_title_v1/` | diagnostic only | not a release partition | diagnostic | not applicable | not applicable |

The primary preflight reports 20,700 outer-train rows and 3,653 outer-test rows; the body/combined policy reports 20,800 and 3,553. The inner partition names and policies do not directly match the new harness names and should not be silently mapped. The manifests are existing evaluation evidence, not approval for the new release.

The existing manifest code can be studied for a future runner, but the current harness intentionally does not consume or modify those manifests. Before reuse, a future task must validate the manifest schema against the exact new input hashes and columns, verify every row/group assignment and overlap, resolve mixed-label and duplicate-key policy decisions, and obtain explicit owner approval for the selected policy. Local hash agreement would establish consistency only, not dataset authenticity or licensing.

## Future real-data runner interface

No real-data runner was implemented or executed. The hardened harness defines the safety boundary a future runner must use:

1. Parse a reviewed configuration and reject unknown fields, missing values, invalid types, non-absolute output roots, contradictory flags, and path-like candidate IDs.
2. Validate the output root under the designated new candidate namespace and reject any existing root, production path, shared evaluation path, traversal, or resolved alias outside the namespace.
3. Require dataset identity, version, exact schema, label mapping, source hashes, reviewed licensing/provenance evidence, source revision, preprocessing revision, approved grouping policy, partition manifest, estimator/vectorizer/calibration configuration, environment record, and candidate ID.
4. Validate the partition manifest before fitting: every row exactly once, every group exactly once, no group overlap, valid labels, non-empty partitions, and accepted class/mixed-label policy.
5. Record the complete configuration and output plan before training. The configured root must equal the validated root.
6. Fit only on the fit partition, select only on the selection partition, calibrate only on the calibration partition, and evaluate once on the frozen final-test partition.
7. Keep real-data execution disabled until reviewed evidence and owner authorization are supplied. The current harness still deliberately refuses real-data training even if those fields are populated.

## Remaining gates

- Dataset origin, licensing, acquisition record, and independent provenance remain unresolved.
- No new-release grouping policy has been approved by the project owner.
- Existing manifests have not been authenticated against a trusted dataset source and are not automatically approved for the new release.
- The complete dependency lock and authenticated environment record remain missing.
- An isolated real-data training/export runner remains to be implemented and separately reviewed.
- No trusted release root, signing process, or authenticated candidate manifest exists.
- Production deployment remains unauthorized.

## Git and safety record

Before the review:

- HEAD: `8c41ae005f4bee178a2b0104cb29049f00182081`
- Branch: `main`
- Pre-existing modified files: `README.md`, `app.py`, `download_models.py`, `frontend/style.css`, `predictor.py`, `routers/api.py`.
- Pre-existing untracked files/directories included prior audit reports, tests, documentation, and the Task 22 candidate namespace.

After the review, HEAD remained `8c41ae005f4bee178a2b0104cb29049f00182081`. Existing changes and untracked paths were preserved. Changes were confined to:

`evaluation_results/new_release_candidate_2026-10-22/harness/`

No real-data training, calibration, evaluation, production artifact loading, production artifact modification, download, installation, signing, deployment, commit, push, tag change, or history change occurred.

**Final status:** adversarial harness review passed for the executed synthetic cases; one Windows symlink test was skipped for an explicit environment reason. The harness is not production-ready and does not authorize real-data execution.
