# Task 24 — Independent Harness Verification Report

**Date:** 2026-10-22  
**Executive result:** **CONDITIONAL PASS**  
**Scope:** Source audit and synthetic tests only. This task did not authorize real-data training or a production release.

## Executive result

The Task 23 hardening was independently confirmed in the actual source and strengthened further. The final harness suite passed **17 tests**, with **1 native symlink test skipped** because this Windows environment does not grant the privilege required to create directory symlinks (`WinError 1314`).

A privilege-independent injected-resolver test now exercises the actual containment decision: a synthetic alias is resolved outside the allowed namespace and the harness rejects it. This verifies the decision logic, but it does not replace native filesystem symlink coverage.

The result is conditional rather than production readiness. Dataset provenance/licensing, owner-approved grouping policy, validated real-data partitions, dependency locking, release authentication, and real-data runner review remain unresolved.

## Baseline

Before changes:

- HEAD: `8c41ae005f4bee178a2b0104cb29049f00182081`
- Branch: `main`
- Existing modified files: `README.md`, `app.py`, `download_models.py`, `frontend/style.css`, `predictor.py`, `routers/api.py`.
- Existing untracked paths included prior audit reports, project documentation, tests, and the Task 22/23 harness namespace.
- Harness files inspected: `isolated_build_harness.py`, `candidate_config.template.json`, `test_isolated_build_harness.py`, and `TASK22_HARNESS_REPORT.md`, `TASK23_HARNESS_HARDENING_REPORT.md`.

Baseline command:

```text
.venv\Scripts\python.exe -m pytest evaluation_results/new_release_candidate_2026-10-22/harness/tests/test_isolated_build_harness.py -q -rs
```

Baseline result:

```text
15 passed, 1 skipped in 0.18s
```

The baseline skip was the native directory-symlink test at `test_isolated_build_harness.py:129` before the new tests were added. The reported reason was Windows `WinError 1314`.

## Source-level verification

| Security claim | Actual implementation | Supporting test | Result |
|---|---|---|---|
| External/custom namespace escape is rejected | `validate_output_root()` requires `allowed_namespace` to resolve inside the designated new harness namespace (`isolated_build_harness.py:76-106`). | `test_traversal_absolute_and_external_namespace_attempts_are_rejected` | Verified. |
| Absolute paths and `..` traversal are contained | `_resolved()` and the containment check are used before path acceptance. | Same traversal test | Verified for tested synthetic paths. |
| Resolved aliases outside the root are rejected | `validate_output_root()` accepts an injected resolver boundary and applies the same containment decision to the resolved path (`:81`, `:92-100`). | `test_injected_resolver_exercising_containment_rejects_external_alias` | Verified through controlled resolution injection. |
| Native symlinks are rejected after resolution | `Path.resolve(strict=False)` is the default resolver. | `test_symlink_alias_to_protected_path_is_rejected_when_supported` | Native test skipped because symlink privilege was unavailable. Not fully verified natively. |
| Existing empty and non-empty output roots are rejected | `validate_output_root()` rejects every existing root (`:105-106`), before creation. | `test_failed_validation_creates_no_artifacts` | Verified. |
| Configuration types and contradictions fail closed | `validate_build_configuration()` rejects unknown fields, non-boolean flags, missing fields, non-absolute output roots, path-like IDs, and synthetic configs enabling real-data training (`:289-323`). | `test_configuration_rejects_types_unknown_fields_and_contradictions` | Verified. |
| Configured root equals validated root | `record_output_plan()` compares the resolved configured path to the validated root (`:124-138`). | Plan-recording and path tests | Verified. |
| Mixed-label policy is explicit | `build_group_split()` rejects mixed groups by default and requires `allow_mixed_label_groups=True` (`:184-214`). | `test_mixed_label_groups_are_explicitly_gated` | Verified. |
| Group disjointness is checked after split | The final report computes pairwise overlap and raises if any overlap exists (`:275-282`). | `test_groups_are_disjoint_and_reported` | Verified on synthetic fixtures. |
| Plan-write failure is cleaned up | `record_output_plan()` removes its own plan file and newly created directory on write failure (`:141-155`). | `test_plan_write_failure_cleans_new_directory` | Verified with injected write failure. |
| Real-data gate cannot be bypassed by a flag | Real data requires reviewed licensing, provenance, and grouping approval evidence, explicit real-data enablement, and the function still deliberately refuses training (`:309-323`, `:328-332`). | `test_unresolved_real_provenance_cannot_be_bypassed_by_flag`, `test_real_training_requires_group_approval_and_partition_manifest` | Verified. |

The source supports fail-closed behavior for the tested conditions. It does not claim protection against a concurrent filesystem race between validation, directory creation, and writing.

## Additional hardening changes

Changes were confined to the permitted harness directory:

- `isolated_build_harness.py`
  - added explicit `source_data_hashes`, `grouping_approval`, and `partition_manifest` requirements;
  - added strict allowed-namespace containment;
  - added an injectable path-resolution boundary for controlled alias testing;
  - bound configuration `output_root` to the validated root;
  - preserved cleanup on plan-write failure;
  - kept explicit mixed-label policy enforcement.
- `candidate_config.template.json`
  - added placeholders for source hashes, grouping approval, and validated partition manifest.
- `tests/test_isolated_build_harness.py`
  - added injected-resolver containment coverage;
  - added real-data grouping-approval/partition-manifest gate coverage;
  - retained the conditional native symlink test;
  - added traversal, configuration, and cleanup regression coverage.
- `TASK24_INDEPENDENT_VERIFICATION_REPORT.md`

No production code, production artifact, previous audit report, or existing evaluation directory was modified.

## Symlink and path-alias strategy

Three levels of evidence are distinguished:

1. **Real filesystem behavior:** all ordinary temporary-directory path tests use actual Windows paths, `Path.resolve(strict=False)`, containment checks, existing-root checks, and `..` traversal attempts.
2. **Controlled resolver boundary:** the injected-resolver test maps a synthetic alias to an outside temporary directory and then invokes the actual `validate_output_root()` containment logic. It is not a constant-answer mock; the security branch makes the rejection decision.
3. **Native directory symlink:** attempted but skipped because the process lacks the Windows privilege required by `os.symlink`. No privilege escalation was requested.

The harness therefore has strong tested path-resolution logic but does not have a successful native Windows symlink test in this environment. A future privileged or developer-mode test environment should run the conditional native test before relying on native symlink behavior operationally.

## Cleanup and failure behavior

Synthetic tests verified that:

- validation failure occurs before candidate directory creation;
- an existing sentinel file is preserved;
- an existing output root is never overwritten;
- a simulated plan-write failure removes the newly created candidate directory;
- path attempts outside the allowed namespace fail before writing; and
- configuration gate failure produces no candidate artifacts.

The implementation documents cleanup as best effort and does not claim immunity to concurrent filesystem races or abrupt process termination at every instruction boundary. A future runner should use an exclusive creation strategy and an activation marker/transaction protocol if it must support crash recovery.

## Regression test results

Final command:

```text
.venv\Scripts\python.exe -m pytest evaluation_results/new_release_candidate_2026-10-22/harness/tests/test_isolated_build_harness.py -q -rs
```

Final result:

```text
17 passed, 1 skipped in 0.20s
```

Skipped test:

```text
directory symlink unavailable in this environment: [WinError 1314] A required privilege is not held by the client
```

No directly relevant existing test outside the harness was run because those suites may read or process the real dataset, which is outside this task’s synthetic-only scope. No test loaded a model artifact.

## Duplicate-aware grouping evidence audit

The existing duplicate-aware implementation was read-only inspected. It declares:

- `all_keys_v1`: title, body, and combined keys;
- `body_combined_only_v1`: body and combined keys; and
- `low_information_title_v1`: a diagnostic for placeholder titles.

It records normalization, transitive component grouping, deterministic split, manifest schema, and reservation algorithms. Existing final reports include:

- primary/all-keys: 24,353 rows, 24,053 groups, 20,700 outer-train rows, 3,653 outer-test rows;
- body/combined-only: 24,353 rows, 24,349 groups, 20,800 outer-train rows, 3,553 outer-test rows; and
- inner partitions named `proper_fit`, `method_selection`, and `final_calibration`.

The policies differ materially in group count and row allocation. The low-information policy is diagnostic rather than an approved release partition. Existing reports contain consistency and split-feasibility evidence, but they are not independently authenticated dataset provenance and do not constitute owner approval for the new release. The harness does not consume or modify them.

Before reuse, a future runner must verify exact source hashes/schema against the new input, validate every row/group assignment and overlap, resolve mixed-label and duplicate-key policy questions, and obtain explicit owner approval. No policy was selected here.

## Remaining security issues and release blockers

- Native Windows symlink behavior remains unexecuted due to missing privilege; the controlled resolver test is not a substitute for that native test.
- The harness does not claim protection from filesystem races or all crash-recovery states.
- Dataset provenance, licensing, acquisition records, and source hashes remain unresolved as release evidence.
- The grouping policy and partition manifest remain subject to owner approval and exact-input validation.
- The dependency environment is not locked or independently authenticated.
- No real-data runner has been implemented or approved.
- No release trust root, signed manifest, or authenticated build process exists.
- Production deployment remains unauthorized.

## Git and scope verification

After the final changes:

- HEAD remains `8c41ae005f4bee178a2b0104cb29049f00182081`.
- All pre-existing modified and untracked paths remain present.
- Changes are confined to `evaluation_results/new_release_candidate_2026-10-22/harness/`.
- No production application, inference, API, deployment, downloader, model artifact, prior report, Git tag, or Git history was modified.

## Explicit safety confirmation

This task did not read the real dataset for training or evaluation, load or deserialize model artifacts, download or install anything, train or calibrate models, create a release manifest, sign files, deploy, commit, push, or authorize production release.

**Final status:** conditional pass for the independently audited synthetic harness cases; native symlink coverage remains environment-limited, and all real-release gates remain open.
