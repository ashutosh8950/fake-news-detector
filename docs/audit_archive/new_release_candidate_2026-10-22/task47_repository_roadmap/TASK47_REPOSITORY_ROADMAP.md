# TruthScan Repository State Audit and Release-Readiness Roadmap

**Audit date:** 2026-10-26  
**HEAD inspected:** `8c41ae005f4bee1782a0104cb29049f00182081`  
**Scope:** read-only repository inspection plus isolated synthetic Track B tests. No model/data execution was performed.

## Executive summary

TruthScan has a useful but fail-closed Track A application and a separately isolated synthetic Track B contract demonstration. The highest-value work that can proceed before dataset and model provenance are resolved is product hardening around explicit boundaries: local startup/readiness behavior, frontend error recovery, API contract documentation, synthetic test organization, and reproducible test execution.

Real Fake/Real inference remains blocked. The application imports model-loading code and attempts readiness during its lifespan, but the inspected tests simulate missing artifacts rather than proving a trusted model build. Track B has no production route, retriever, model, or external evidence source.

The immediate recommendation is to improve the **verification surface** without changing inference behavior: establish a narrowly scoped, model-free local smoke-test harness and make the API/frontend readiness contract machine-readable and maintainable. This can be done without datasets, artifacts, package installation, or release-gate changes.

## Repository state and evidence

### Directly verified in this audit

- `app.py` creates the FastAPI application, mounts the frontend, includes `routers.api`, and defines a lifespan that calls model-loading and spaCy/DistilBERT preparation paths.
- `routers/api.py` exposes `/health`, `/models/info`, `/metrics`, `/analyze`, and `/analyze/deep`. `/health` returns HTTP 503 and `not_ready` when `predictor.loaded` is false. `/analyze` returns HTTP 503 with `Inference unavailable: trusted model artifacts are not ready.` when the ensemble is unavailable.
- `AnalyzeRequest` enforces a maximum title/text length and a minimum 20-character article text after whitespace stripping.
- The global exception handler returns a bounded user-facing error and request ID rather than a traceback.
- The frontend contains a separate response contract module and explicit branches for offline API, unavailable models, malformed responses, and hidden stale results, as asserted by `tests/test_application_e2e.py` and `tests/test_frontend_response_contract.py`.
- The current Track B prototype files are under `evaluation_results/new_release_candidate_2026-10-22/task44_synthetic_prototype/`. Its Python module has no FastAPI registration, network client, dataset reader, model loading, or evidence retriever.
- Track B permits only `SUPPORTED`, `REFUTED`, and `INSUFFICIENT_EVIDENCE`; positive outcomes require evidence, while insufficient evidence requires an empty evidence list.
- The synthetic demonstration contains three hand-authored examples, synthetic provenance identifiers, and tests for all three outcomes and invalid evidence handling.
- The checked-in CI workflow targets Ubuntu with Python 3.11, installs `requirements-ci.lock` without hash enforcement, and runs the listed synthetic/core pytest suite.
- `git diff --check` was run after inspection; it reported only existing line-ending normalization warnings.

### Static conclusions

- Track A and Track B are separate in the current source tree: the live application source does not import `synthetic_claim_api`, and the inspected Track A route set contains no claim-verification route.
- The current Track A readiness path is truthful when the model bundle is unavailable, but a normal application lifespan still enters model and preprocessing load paths. A safe local verification harness should continue to mock or isolate these paths rather than rely on accidental artifact absence.
- The current frontend tests are partly source-level assertions. They provide useful contract protection but are not browser-level evidence.
- Track B metadata validation establishes schema shape and bounded strings; it does not authenticate a source, prove licensing, or establish that evidence is true.

### Previously reported, not reverified in full here

- Task 54–56 reports state that the existing environment's core suites passed and that clean hash-pinned installation remains blocked. Those reports were read as project evidence, not independently rerun in this audit.
- Task 27 and later reports state that the existing datasets have no authenticated upstream mapping or sufficient rights evidence.
- Historical model-artifact and release-root reports state that the historical artifacts are not independently authenticated.
- The historical 98.44% metric remains reported evidence, not a verified release or generalization claim.

## Current readiness assessment

| Area | Status | Evidence-based explanation |
|---|---|---|
| Track A application shell | `PARTIALLY_READY_FOR_LOCAL_INSPECTION` | Routes, frontend, bounded errors, and unavailable-model behavior are implemented and covered by tests, but real readiness and inference are intentionally unavailable without trusted artifacts. |
| Track A model inference | `BLOCKED_INSUFFICIENT_EVIDENCE` | Dataset rights, model provenance, dependency reproducibility, and release trust roots remain unresolved. |
| Track B contract | `SYNTHETIC_ONLY` | Contract, validator, UI mockup, demonstration, and 20 isolated tests exist; no retriever or model exists. |
| Track B real claim verification | `NOT_IMPLEMENTED` | No evidence retrieval, source authentication, real FEVER data, or adjudication path exists. |
| CI reproducibility | `CONDITIONAL` | Exact pins and a configured workflow exist, but prior reports record no approved package mirror, no complete retained distributions, and no clean hash-enforced installation. |
| Public release | `BLOCKED` | Rights, artifacts, dependencies, trust roots, security/release approval, and deployment authorization remain unresolved. |

## Prioritized engineering roadmap

Estimates are approximate agent working time after prerequisites are available. External owner/legal/package-source waiting time is separate and not estimated.

### 1. Build a model-free local readiness smoke-test harness

**Value:** Makes the most important current user experience—“application available, inference unavailable”—easy to verify and demonstrate without artifacts.

**Components:** `app.py`, `routers/api.py`, `frontend/index.html`, `frontend/app.js`, `tests/test_application_e2e.py`, and a small test-only fixture or harness.

**Dependencies/blockers:** No dataset or model needed. Must avoid importing or invoking real artifact loads beyond controlled mocks.

**Safety risk:** A test harness could accidentally create a false-ready state; keep all model readiness mocked to false and assert no prediction fields are returned.

**Acceptance criteria:** fresh test invocation verifies `/`, `/health` 503, `/analyze` 503, bounded error text, no Fake/Real result, and frontend unavailable/offline branches. No production route changes.

**Estimate:** 3–5 agent-hours.  
**Can proceed now:** Yes.

### 2. Add a browser-independent frontend state contract fixture suite

**Value:** Strengthens validation of loading, stale-result clearing, malformed responses, offline API, retry, and unavailable-model states while browser tooling is unavailable or unverified.

**Components:** `frontend/app.js`, `frontend/response_contract.js`, `tests/test_frontend_response_contract.py`, and possibly a small static DOM test seam if it can be added without dependencies.

**Dependencies/blockers:** Existing Node/Python test environment; no browser package installation.

**Safety risk:** Tests must not broaden accepted response shapes or permit malformed data to render a prediction.

**Acceptance criteria:** synthetic cases assert state transitions and rejected payloads; Track A accepts only its documented Fake/Real contract; no Track B labels are accepted.

**Estimate:** 4–7 agent-hours.  
**Can proceed now:** Yes.

### 3. Make the API readiness and response contracts explicit in one maintained specification

**Value:** Reduces drift between FastAPI schemas, frontend validation, README instructions, and future portfolio demonstrations.

**Components:** `routers/api.py`, `frontend/response_contract.js`, `README.md`, API docs metadata, and a small contract test module.

**Dependencies/blockers:** Must preserve current Track A response compatibility; no model required.

**Safety risk:** Documentation or schema changes could accidentally imply model readiness or change client behavior.

**Acceptance criteria:** documented status codes and fields match actual routes; 503 readiness behavior and 422 validation behavior are tested; Track B remains explicitly excluded from production OpenAPI routes.

**Estimate:** 3–5 agent-hours.  
**Can proceed now:** Yes.

### 4. Separate startup diagnostics from model readiness in local development

**Value:** Makes local startup understandable when artifacts are absent and prevents operators from confusing a running web server with ready inference.

**Components:** `app.py`, `config.py`, `README.md`, startup tests, and possibly logging assertions.

**Dependencies/blockers:** Requires careful review of current lifespan behavior; no real artifacts should be loaded during tests.

**Safety risk:** Do not bypass `artifact_contract.py`, suppress integrity failures, or mark `models_loaded` true.

**Acceptance criteria:** documented local command; startup can remain available for `/` and diagnostics; `/health` remains not-ready on missing/invalid artifacts; user-facing errors remain bounded; integrity failures are visible in controlled logs.

**Estimate:** 4–8 agent-hours.  
**Can proceed now:** Yes, with mocked readiness tests.

### 5. Package the synthetic Track B demonstration as a clearly named test/demo target

**Value:** Provides a concise portfolio/interview walkthrough without implying real fact-checking capability.

**Components:** `synthetic_evidence_demo.py`, `test_synthetic_evidence_demo.py`, `TASK46_SYNTHETIC_EVIDENCE_DEMO.md`, and CI command documentation.

**Dependencies/blockers:** None beyond the existing Python environment.

**Safety risk:** Synthetic source IDs and claims must remain visibly synthetic; no production route or FEVER data should be added.

**Acceptance criteria:** one documented command prints all three outcomes; tests assert synthetic markers, abstention, invalid evidence rejection, and Track A conversion refusal.

**Estimate:** 1–3 agent-hours.  
**Can proceed now:** Yes; most of this task is already implemented and should be maintained rather than rewritten.

### 6. Establish a safe test classification and CI boundary

**Value:** Prevents accidental execution of model-dependent, dataset-dependent, or calibration tests in synthetic CI.

**Components:** `.github/workflows/ci.yml`, `requirements-ci.lock`, pytest configuration if present, and test markers or selection lists.

**Dependencies/blockers:** Dependency-source and hash-pinning blocker remains unresolved for full reproducibility.

**Safety risk:** A broad test command could load artifacts or touch datasets; selection must remain explicit and reviewed.

**Acceptance criteria:** CI lists only safe tests; model/data tests are visibly excluded; local equivalent command is documented; remote CI remains labeled unverified until it actually runs.

**Estimate:** 3–6 agent-hours.  
**Can proceed now:** Partially; test classification can proceed, hash-pinned reproducibility cannot.

### 7. Resolve the approved dependency-source path and hash-enforced CI lock

**Value:** Enables clean-machine reproduction and makes future candidate builds defensible.

**Components:** `requirements-ci.lock`, `.github/workflows/ci.yml`, `TASK55_HASH_PINNED_DEPENDENCY_REPORT.md`, and package-source policy.

**Dependencies/blockers:** Requires owner-provided approved mirror or complete target-platform distributions for Python 3.11/Linux.

**Safety risk:** Never invent hashes, silently use an unapproved source, or weaken `--require-hashes`.

**Acceptance criteria:** hashes derive from actual installable distributions; fresh install succeeds; `pip check` and safe suite pass; package source and remote CI status are recorded separately.

**Estimate:** 4–8 agent-hours after source access is available; waiting time unknown.  
**Can proceed now:** No, beyond preparing the owner request.

### 8. Define Track B source/provenance interfaces using synthetic adapters

**Value:** Advances the future FEVER-compatible architecture without acquiring FEVER or connecting a live source.

**Components:** isolated Track B directory, contract documentation, synthetic tests, and a future adapter interface.

**Dependencies/blockers:** Real adapter requires owner rights decision, exact source/revision, applicable terms, and approved evidence-retention policy.

**Safety risk:** Synthetic adapters must never be mistaken for evidence retrieval or source authentication.

**Acceptance criteria:** interface includes source ID, canonical reference, version/snapshot, retrieval timestamp, excerpt bounds/hash, license notice, and failure/abstention states; no network calls in unit tests.

**Estimate:** 5–9 agent-hours.  
**Can proceed now:** Interface only, yes; real source integration, no.

### 9. Create the candidate-build and evaluation evidence schema

**Value:** Ensures any eventual model build has reproducible dataset, split, dependency, artifact, evaluation, and trust-root records.

**Components:** existing provenance/release-plan directories, `artifact_contract.py`, manifest helpers, and documentation—without changing current gates.

**Dependencies/blockers:** Exact approved dataset/source, model, dependency source, and owner evaluation policy remain unavailable.

**Safety risk:** Do not use the schema as evidence that a candidate is approved; do not load or generate artifacts.

**Acceptance criteria:** schema fields cover source identity, digests, transformation receipt, split policy, code commit, dependency lock, model files, signatures/attestations, metrics, and scope approval; missing fields fail closed.

**Estimate:** 5–10 agent-hours.  
**Can proceed now:** Schema design can proceed; populated release record cannot.

### 10. Owner decision gate for real data/model work

**Value:** Prevents engineering effort from silently crossing into unauthorized acquisition or release activity.

**Components:** `FEVER_DECISION_READINESS.md`, `MODEL_RELEASE_PREREQUISITES.md`, dataset decision records, and release checklists.

**Dependencies/blockers:** Owner and qualified rights/release review.

**Safety risk:** A “yes” to assessment must not be interpreted as approval for acquisition, training, model distribution, or hosting.

**Acceptance criteria:** owner records separate decisions for dataset assessment, training, internal evaluation, model distribution, public inference, commercial use, and raw/transformed-data redistribution.

**Estimate:** 1–2 engineering hours to record; external waiting time unknown.  
**Can proceed now:** No; requires owner input.

## Blockers requiring owner or external evidence

1. Existing `Fake.csv`/`True.csv` provenance and rights are unresolved.
2. No approved replacement dataset or FEVER acquisition scope exists.
3. Historical model artifacts and release trust roots are not independently authenticated.
4. The dependency lock has exact pins but no verified hash-enforced clean installation; no approved mirror or retained target distributions were evidenced.
5. Public inference, model distribution, commercial use, and raw/transformed-data redistribution are not authorized.
6. Browser-level behavior and remote CI execution remain unverified.

## Remaining engineering effort

Before external approvals, approximately **18–35 agent-hours** can be spent on the model-free readiness harness, frontend state contracts, API documentation, startup diagnostics, synthetic Track B packaging, CI test classification, and provenance-schema interfaces.

After approved data/source, dependency distributions, artifacts, and review decisions are available, approximately **25–55 additional agent-hours** may be needed for reproducible candidate-build integration, evidence-aware Track B work, evaluation, and release evidence. This excludes model training time, package/source waiting, legal review, and deployment operations.

These estimates assume the current architecture is retained and no large frontend or backend rewrite is required.

## Recommended immediate next task

Implement Task 1: a model-free local readiness smoke-test harness. It has the highest immediate user and portfolio value, directly exercises the current fail-closed behavior, requires no unresolved data or artifacts, and can produce evidence that `/` works while `/health` and `/analyze` correctly refuse inference. Keep it entirely test-only and preserve the current production readiness gates.

## Commands and results

Executed:

```text
git rev-parse HEAD
git status --short
python -m unittest -v test_synthetic_claim_api.py test_synthetic_evidence_demo.py
git diff --check
```

Observed:

- HEAD: `8c41ae005f4bee1782a0104cb29049f00182081`.
- The working tree already contained numerous tracked modifications and untracked reports; they were preserved.
- Isolated synthetic suite: **20 tests passed** in `0.009s`.
- `git diff --check`: no content errors; existing CRLF normalization warnings were reported for previously modified files.
- No model-dependent, dataset-dependent, application-startup, or browser tests were executed in this audit.

## Limitations

- This report does not independently reproduce the earlier 54/60-test application results.
- No browser automation was available or used.
- No real model readiness or inference was tested.
- No dataset rows, FEVER files, external evidence, or package distributions were accessed.
- Static source inspection cannot prove deployment behavior or rights clearance.

## Conclusion

The repository is suitable for continued model-free reliability and demonstration work, but not for real inference release. The safest next implementation is a controlled local readiness smoke-test harness, followed by frontend state-contract hardening. Track B should remain synthetic-only until owner-approved source rights, a permitted evidence source, trusted artifacts, reproducible dependencies, and separate release authorization exist.
