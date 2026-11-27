# Task 33 — Gated Candidate Build Report

## Executive result

**PASS for candidate-only orchestration hardening; real-data training and release remain BLOCKED.**

The repository now has one documented candidate orchestration path,
`gated_candidate_build.py:run_gated_preflight`. It delegates to the Task 31
secure boundary, rejects caller authorization fields and legacy evidence, and
never contains a training, calibration, model-loading, or artifact-writing
stage. Direct legacy script invocation with the explicit candidate/release mode
flag refuses before importing training dependencies.

This is an architectural safeguard against accidental or unsupported candidate
execution. It is not a security boundary against a local user who can edit the
source or call arbitrary internal functions.

## Baseline and final repository state

Initial HEAD: `8c41ae005f4bee178a2b0104cb29049f00182081` on `main`.

Pre-existing tracked modifications and untracked files were preserved. The
Task 33 changes are the two explicit candidate-mode guards in `train.py` and
`phase2_calibration.py`, plus the files in this directory. Final HEAD is
unchanged. Final status was inspected after testing; no reset, clean, stash,
commit, push, tag, or deployment was performed.

## Execution paths inspected

Before this task, `train.py:train` could read data, fit estimators, and write
`models/`; `phase2_calibration.py:main` could read calibration inputs, fit
calibrators, and write `models/calibrated/`. Neither called secure preflight.
The Task 31 boundary called only `run_preflight_secure` and its `invoke_build`
function was already a fail-closed stub.

The new orchestrator imports only the Task 31 boundary. It does not import or
invoke either legacy `main()` function. Its only CLI operation is a dry-run
configuration inspection; no execute mode exists. The legacy scripts retain
ordinary development behavior when invoked without the explicit candidate flag,
but `--candidate-release` and `--release-candidate` refuse with an exit status
before their training/calibration imports.

## Gates and current blockers

The orchestrator requires the secure evidence schema, externally provisioned
expected source/file digests, an externally provisioned public-key root, and an
expected policy configuration before calling the Task 31 boundary. Secure
exceptions and refusals become non-authorizing results. A synthetic or strict
preflight pass still returns `training_permitted=false`, `build_authorized=false`,
and `artifacts_created=false`.

Real execution remains blocked because the project still lacks authenticated
production trust roots and release approval, independently established dataset
provenance/licensing, owner-approved grouping and partition evidence, and a
complete authenticated dependency/environment record. These were not created
or inferred in Task 33.

## Tests run

Task 33 synthetic tests exercised missing roots/digests, legacy evidence,
caller-injected booleans, secure failure/exception, synthetic-key refusal,
post-preflight non-authorization, dry-run path/configuration failures, direct
legacy candidate-mode refusal, and absence of legacy imports/calls. The exact
command was:

`python -m unittest discover -s evaluation_results/new_release_candidate_2026-10-22/task33_gated_build -p "test_*.py" -v`

Result: **9 passed, 0 failed**.

The requested regression suites for Tasks 32, 31, 30, 29, 28, and the isolated
harness were run without training or model loading:

- Task 32: `python -m unittest discover -s .../task32_red_team -p "test_*.py"` — **13 passed**.
- Task 31: `python -m unittest discover -s .../task31_secure_integration -p "test_*.py"` — **21 passed**.
- Task 30: `python -m unittest discover -s .../task30_gate_security -p "test_*.py"` — **13 passed**.
- Task 29: `python -m unittest discover -s .../task29_gate_integration_audit -p "test_*.py"` — **9 passed**.
- Task 28: `python -m unittest discover -s .../task28_runner_preflight -p "test_*.py"` — **17 passed**.
- Harness: `python -m pytest evaluation_results/new_release_candidate-2026-10-22/harness/tests/test_isolated_build_harness.py -q` — **17 passed, 1 skipped**. The skip is the existing privilege-dependent native Windows symlink test.

An initial attempt to discover the pytest-based harness with `unittest`
reported “NO TESTS RAN”; it was not counted as a pass, and the suite was then
run with its actual pytest runner.

## Compatibility and limitations

This change intentionally preserves ordinary non-release development calls to
the historical training and calibration scripts. A developer who invokes
those functions without candidate mode can still perform ordinary local work;
that is not claimed to be a secure release path. A local operator with source
write access can also bypass Python-level guards by modifying code or invoking
internal functions directly. Future real-data execution must be added only as
a reviewed implementation behind the single orchestrator, never by reusing
the legacy script mains.

No real data, model artifacts, calibration outputs, release artifacts, trust
roots, approvals, or signatures were loaded, created, or modified.

## Work remaining

The next task should provision and independently authenticate real trust roots,
resolve dataset provenance/licensing, approve the grouping and partition
evidence, establish a defensible dependency/environment record, and design the
reviewed future training stage behind this boundary. Approximate duration for
that evidence-and-design work is one to two working days; a complete controlled
rebuild and release review would require additional time after those inputs are
available. No estimate here authorizes training or deployment.
