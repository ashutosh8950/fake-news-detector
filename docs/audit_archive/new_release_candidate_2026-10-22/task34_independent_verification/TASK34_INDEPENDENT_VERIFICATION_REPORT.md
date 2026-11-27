# Task 34 — Independent Verification Report

## Executive result

**PASS for the inspected candidate-only safeguards, with documented limitations.**

The Task 33 implementation was independently inspected and its key refusal
claims were reproduced with synthetic fixtures and safe subprocesses. The
orchestrator routes through the Task 31 secure boundary, rejects missing roots,
legacy evidence, injected authorization fields, and synthetic keys, and keeps
all authorization and artifact flags false. Direct invocation of the legacy
scripts with the documented candidate/release flags refuses before training
dependencies are imported.

This does not make ordinary local execution impossible. Without candidate flags,
`train.py` and `phase2_calibration.py` retain their historical development
entry points and can fit/write artifacts if a local operator explicitly calls
them. That compatibility behavior is outside the supported candidate-release
path and remains a material architectural limitation.

## Baseline and final repository state

Initial HEAD: `8c41ae005f4bee178a2b0104cb29049f00182081`.

Initial working-tree status contained the existing modifications to
`README.md`, `app.py`, `download_models.py`, `frontend/style.css`,
`predictor.py`, `routers/api.py`, `train.py`, and `phase2_calibration.py`, plus
the previously existing untracked documentation, tests, and evaluation
directories. No reset, clean, stash, commit, push, deploy, or history change
was performed.

Final HEAD is unchanged. The only files created by this task are inside
`task34_independent_verification/`; prior files and changes were preserved.

## Source-level verification

Verified facts:

- `gated_candidate_build.py:run_gated_preflight` imports and calls
  `secure_build_boundary:candidate_preflight_only`, not the Task 28 legacy
  function or either legacy script.
- The orchestrator requires the Task 30 schema, nonempty external digest
  mappings, an external public-key mapping, and expected policy configuration.
- It rejects caller fields such as `training_permitted`, `build_authorized`,
  `approved`, and `authenticated`.
- Boundary exceptions and secure refusals become non-authorizing results.
- The post-boundary result explicitly keeps `training_permitted`,
  `build_authorized`, and `artifacts_created` false.
- `dry_run_config` only parses a JSON configuration under the Task 33 root and
  returns documented blockers; it does not read dataset rows or create output
  directories.
- The top-level guards in `train.py` and `phase2_calibration.py` run before
  their training/calibration imports and refuse `--candidate-release` and
  `--release-candidate`.

The Task 31 boundary itself calls `run_preflight_secure`; its strict production
mode remains fail-closed because no production trust-root provisioning exists.

## Adversarial tests

The Task 34 suite contains 16 tests covering direct legacy candidate-mode
refusal, missing roots, injected authorization, legacy schemas, secure failure
and exception handling, synthetic keys, changed bound inputs, missing evidence
categories, boundary routing, import side effects, dry-run isolation, strict
success without authorization, lower-level import exclusion, malformed JSON,
and path escape.

Command:

`python -m unittest discover -s evaluation_results/new_release_candidate_2026-10-22/task34_independent_verification -p "test_*.py" -v`

Result: **16 passed, 0 failed**.

No test invoked `train.py:train`, `phase2_calibration.py:main`, model loading,
real-data evaluation, or artifact generation.

## Regression suites

- Task 33: **9 passed**.
- Task 32: **13 passed**.
- Task 31: **21 passed**.
- Task 30: **13 passed**.
- Task 29: **9 passed**.
- Task 28: **17 passed**.
- Existing harness: **17 passed, 1 skipped** using pytest. The skip is the
  existing privilege-dependent native Windows symlink test.

The harness was run with:
`python -m pytest evaluation_results/new_release_candidate-2026-10-22/harness/tests/test_isolated_build_harness.py -q`

## Findings and limitations

No bypass was demonstrated within the supported candidate-only path. A valid
synthetic boundary result still cannot authorize training. Legacy preflight
results cannot pass the orchestrator schema and authorization checks.

The following are not proven by this task:

- That real production trust roots, signatures, licensing, provenance, or owner
  approvals exist; they do not currently exist in the repository evidence.
- That native symlink handling is fully exercised without Windows symlink
  privileges.
- That arbitrary direct calls to legacy functions are technically impossible;
  they are not. The Python guards are architectural safeguards, not a defense
  against a local source editor.
- That a future real-data runner is safe; no such runner exists or was run.

## Release status and recommendation

The current implementation cannot authorize real-data training or release:
`training_permitted=false`, `build_authorized=false`, and
`artifacts_created=false` remain enforced in the inspected candidate path.

The next task should obtain independently authenticated dataset provenance and
licensing, owner-approved grouping/partition evidence, a defensible dependency
and environment record, production trust roots, and explicit release approval.
Only after those external gates are resolved should a reviewed real-data build
stage be designed behind this preflight boundary.
