# Task 28 — Candidate Runner Preflight Report

## Result

**PASS for preflight implementation and synthetic-test quality.** The new module refuses missing, malformed, mismatched, stale, unapproved, unsigned, and unsafe evidence. A synthetic complete-evidence case reaches `PREFLIGHT_PASS_STOPPED_BEFORE_TRAINING`, with `training_permitted: false`, no candidate directory, and no model artifacts. This does not establish dataset provenance/licensing, owner approval, dependency reproducibility, release authentication, or production readiness.

## Baseline and final repository state

- HEAD before and after: `8c41ae005f4bee178a2b0104cb29049f00182081`.
- Existing modified tracked files and untracked paths were preserved.
- New files are confined to `evaluation_results/new_release_candidate_2026-10-22/task28_runner_preflight/`.
- No production code, dataset, model artifact, prior report, or existing manifest was modified.

## Implementation

`candidate_runner_preflight.py` provides:

- strict evidence schema and SHA-256 shape validation;
- dataset path/hash set consistency and explicit identity approval;
- reviewed provenance/licensing evidence covering training, artifact distribution, and hosting;
- approved grouping policy and exact configuration fingerprint;
- partition-manifest hash, certificate hash, policy identity, and source-data fingerprint consistency;
- explicit group-disjointness, coverage, and leakage results;
- reviewed Python/platform/environment evidence with an accepted lock status;
- runner containment, overwrite protection, and cleanup evidence;
- distinct-new-release authorization requiring an authenticated evidence reference;
- stale-result detection through a canonical evidence fingerprint;
- refusal of existing output roots, traversal/alias escapes, shared evaluation paths, and production model paths;
- report writing only below an existing approved report root, with overwrite refusal and temporary-file cleanup.

The implementation never imports training, preprocessing, spaCy, joblib, pickle, or the production predictor. It never reads dataset rows and never creates a candidate output directory. The `write_gate_report` helper writes only an explicitly approved report and is not a training stage.

## Enforced versus documented controls

| Control | Status | Evidence |
|---|---|---|
| Dataset identity and SHA-256 fields | Enforced structurally | `run_preflight` validates paths, hash format, set equality, and approval source |
| Provenance/licensing intended-use coverage | Enforced structurally | Requires reviewed status, evidence source, approval, and all three declared uses |
| Grouping policy/fingerprint | Enforced | Requires approval, valid fingerprint, and optional expected-fingerprint match |
| Manifest/certificate/source consistency | Enforced structurally | Requires hashes, policy match, certificate status, and derived source fingerprint |
| Partition integrity | Enforced as supplied verification results | Requires explicit true values for disjointness, coverage, leakage, and approval; it does not recompute real manifests |
| Environment/lock evidence | Enforced as supplied acceptance | Requires reviewed record, Python/platform/source, and `complete` or `accepted_with_limitations`; it does not authenticate a lock |
| Runner path isolation | Enforced for output/report paths | Resolves paths, requires approved namespace, rejects existing roots and protected paths; filesystem races are not claimed to be eliminated |
| Release authentication | Enforced only as an evidence gate | Requires `authenticated: true` and a source, but no cryptographic signature verifier or trusted-key store exists |
| Training execution | Refused by design | Synthetic pass returns `training_permitted: false` and stops |
| Real source-data validation | Not implemented here | Requires a future separately reviewed runner and approved manifest reader |

The release-authentication field is intentionally not treated as proof by itself. A local editable JSON record can satisfy the shape only in synthetic tests; a real deployment requires an organization-controlled trust root and verification implementation. Current Task 26–27 records remain unapproved/blocked and cannot satisfy this gate.

## Synthetic adversarial tests

Command:

```text
python -m unittest discover -s evaluation_results/new_release_candidate_2026-10-22/task28_runner_preflight -p "test_*.py" -v
```

Result: **17 passed, 0 failed**.

Cases covered include missing provenance/licensing, unapproved policy, wrong fingerprint, source-hash mismatch, malformed certificate, incomplete partition integrity, stale environment status, missing release authorization, unsigned editable approval, unsafe/traversal/output-root paths, existing non-empty roots, malformed object/type fields, stale prior results after input change, missing dataset hashes, synthetic all-gates pass without training, and report-writer escape/overwrite attempts.

Relevant existing harness command:

```text
python -m pytest evaluation_results/new_release_candidate_2026-10-22/harness/tests/test_isolated_build_harness.py -q
```

Result: **17 passed, 1 skipped**. The skip is the existing environment-dependent symlink case documented by Task 24; no attempt was made to bypass it.

## Machine-readable examples

- `CANDIDATE_PREFLIGHT_TEMPLATE.json` defaults every approval and verification field to refusal values.
- `BLOCKED_PREFLIGHT_EXAMPLE.json` demonstrates a blocked provenance gate and zero side effects.
- `SYNTHETIC_PREFLIGHT_PASS_EXAMPLE.json` demonstrates that even a synthetic all-gates result remains stopped before training.

## Remaining blockers

The following remain unresolved and were not waived:

1. Dataset provenance, licensing, and intended-use authorization from Task 27.
2. Owner approval of the grouping policy and exact partition manifests from Task 26.
3. A complete or independently accepted dependency/environment record from Task 25.
4. A cryptographically verifiable release trust root and signed manifest process.
5. A future real-data runner that independently reads and verifies approved manifests before any build.
6. Native filesystem race and symlink behavior beyond the synthetic/previously tested boundaries.

## Safety confirmation

No real dataset content was processed for model development. No model was loaded, trained, evaluated, downloaded, or serialized. No release artifact or candidate output directory was created. The passing synthetic evidence is not authorization for real-data execution or deployment.
