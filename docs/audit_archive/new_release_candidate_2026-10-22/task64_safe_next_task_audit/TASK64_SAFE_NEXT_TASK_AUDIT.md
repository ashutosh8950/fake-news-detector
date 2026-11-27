# Task 64 — Safe Remaining-Work Audit and Next-Task Selection

**Audit date:** 2026-10-27  
**Current release posture:** `NO-GO` for public Fake/Real inference  
**Decision-dependent work:** on hold pending owner response

## Executive summary

The repository has a substantial model-free readiness and documentation foundation, but the release blockers recorded in Task 57 remain unresolved. The owner has not selected an intended-use scope, dataset path, FND-LRIL continuation option, public-inference scope, commercial scope, distribution scope, or accountable reviewers. Historical model artifacts and the existing datasets remain untrusted for new model work.

The highest-value task that can proceed safely is a bounded **model-free application security and privacy readiness slice**. It should inspect and test the current Track A request path, frontend error handling, logging/error disclosure, retention assumptions, abuse controls, and Track A/Track B separation without loading models, accessing datasets, or enabling inference. This directly addresses part of blocker B-09 and produces actionable evidence for a future release review.

This is a task selection recommendation only. It was not implemented in Task 64.

## Evidence and current state

### Directly inspected in this audit

- The five required decision/blocker records exist and were read:
  - Task 57 blocker register and critical-path memo.
  - Task 58 owner decision gate.
  - Task 59 owner decision checkpoint.
  - Task 63 FND-LRIL continuation decision gate.
- The current Git HEAD is `8c41ae005f4bee178a2b0104cb29049f00182081`.
- The working tree already contains extensive tracked modifications and untracked project/report files. These pre-existing changes were preserved.
- The repository contains model-free smoke tests, a safe local verification script, frontend response-contract tests, and the isolated synthetic Track B prototype.

### Inherited project evidence

Task 57 records nine unresolved release areas: dataset/article rights, third-party content rights, downstream-use scope, historical artifact authenticity, dependency reproducibility, dataset provenance, the `production_switch` conflict, fresh authorized evaluation, and production security/privacy/monitoring/abuse controls. No blocker is marked cleared.

Task 58 and Task 59 keep all owner choices pending and maintain `NO-GO` for public Fake/Real inference. Task 63 separately keeps the FND-LRIL path at `PENDING OWNER DECISION` and does not upgrade its `INSUFFICIENT EVIDENCE` status because of the related MMIFND paper.

These are inherited report findings, not new model or dataset experiments.

## Remaining work grouped by blocker

### Safe to complete now

1. **Model-free application security/privacy readiness slice.** Review and test input limits, error responses, secret/traceback leakage, request logging, retention assumptions, rate/abuse controls, and Track A/Track B import boundaries using synthetic requests only. This is the recommended next task.
2. **Model-free frontend recovery and accessibility coverage.** Extend existing tests for offline API, HTTP 503, malformed responses, stale-result clearing, loading-state recovery, keyboard/focus behavior, and accessible error messaging. Do not produce a prediction.
3. **Synthetic Track B maintenance.** Continue contract, evidence-schema, hostile-string, and demonstration tests. Keep the prototype outside production routing and label all output synthetic.
4. **Documentation consistency check.** Reconcile the README, safe-local-verification instructions, readiness contracts, and release documents without changing production behavior or claiming release approval.
5. **Static production-boundary inspection.** Confirm that no production route imports Track B, no model/data path is invoked by model-free tests, and no deployment path exposes the prototype.

### Blocked by owner decision

- Select intended-use scope: academic-only, local portfolio, public non-commercial, or commercial-capable.
- Select the dataset direction: recover existing provenance, continue FND-LRIL documentation review, choose another candidate, or pause.
- Decide whether public visitor-submission inference is required.
- Decide whether trained weights or raw/transformed data must be distributed.
- Decide whether commercial use is in scope.
- Assign rights, artifact, evaluation, security/privacy, and deployment reviewers.
- Decide whether to continue, hold, or reject FND-LRIL under Task 63.
- Define the meaning or retirement policy for the historical `production_switch` field.

### Blocked by dataset rights/provenance

- Acquire or retain a replacement dataset.
- Inspect or process candidate rows/article text.
- Train or fine-tune a new Track A model.
- Establish a source-grouped, duplicate-resistant, time-aware evaluation on authorized data.
- Generate a new model artifact or claim fresh performance.
- Enable genuine local or public inference based on newly trained data.

### Blocked by artifact authenticity or reproducibility

- Load historical serialized model artifacts as trusted inputs.
- Use historical accuracy/calibration outputs as release evidence.
- Complete a clean hash-enforced CI installation until an approved package source or retained distribution set exists.
- Promote or publish a model bundle without an independent trust root, manifest, compatibility evidence, and release approval.

### Requires explicit release authorization

- Turn on public Fake/Real inference.
- Deploy or publish the application.
- Distribute model weights, datasets, or transformed data.
- Accept visitor text under a public retention/privacy policy.
- Treat any model output as a production fact-checking result.

## Recommended next task

### Bounded model-free application security and privacy readiness slice

**Goal:** produce evidence that the current unavailable-model application state and API/UI boundary do not expose sensitive implementation details, retain submitted content unexpectedly, misrepresent failures as predictions, or accidentally connect Track B to production.

**Likely files/components:**

- `app.py`
- `routers/api.py`
- `frontend/app.js`
- `frontend/response_contract.js`
- `frontend/index.html`
- `tests/test_api.py`
- `tests/test_application_e2e.py`
- `tests/test_frontend_response_contract.py`
- `tests/smoke/test_local_readiness_smoke.py`
- `tests/smoke/README.md`
- `scripts/run_safe_local_verification.ps1`

**Safe test scope:** synthetic short and boundary-length inputs, malformed requests, HTTP 422/503/error paths, unavailable-model responses, offline-style failures, hostile text, and import/call-path inspection. Tests must not read CSV rows, load pickle/joblib files, call external services, or invoke real inference.

**Acceptance criteria:**

1. User-facing errors contain no traceback, secret, absolute path, model filename, or environment value.
2. Input validation and size limits fail in a controlled way.
3. The unavailable-model state cannot produce a Fake/Real label or confidence value.
4. Failed requests clear stale results and restore controls where the current UI supports them.
5. No submitted article text is persisted or logged unexpectedly, or the exact current behavior is documented for review.
6. Rate/abuse protections and retention behavior are either evidenced or explicitly recorded as release gaps; they must not be implied to exist.
7. Track B is not imported by production routes and cannot be enabled by an ordinary configuration value.
8. Focused model-free tests pass, with exact commands and counts recorded.
9. Production source changes are avoided unless a concrete, reproducible defect is found; any fix is minimal and separately tested.

**Estimated engineering effort:** approximately 4–8 agent-hours, assuming the current test infrastructure is usable and no production defect requires broader changes. External waiting time is not expected for the model-free portion, but owner/security review remains separate.

**Why this is the best next task:** it addresses an acknowledged public-release blocker without depending on dataset rights, model artifacts, package-source approval, or owner selection of a candidate. It improves the demonstrability and safety evidence of the application while preserving fail-closed behavior.

## Approximate remaining timeline

These are planning estimates, not commitments or authorization:

| Workstream | Engineering effort after prerequisites | External dependency |
|---|---:|---|
| Model-free security/privacy readiness slice | 4–8 hours | Reviewer availability; no dataset/model dependency |
| Frontend recovery/accessibility hardening, if gaps remain | 3–8 hours | Browser availability for genuine UI checks |
| Owner scope and candidate decision | 1–3 hours | Owner response |
| Rights/provenance review and permission pathway | 4–12+ hours | Rights-holder/qualified-reviewer response; duration unknown |
| Approved dependency lock and clean install | 4–10 hours | Approved mirror or retained distributions |
| Authorized evaluation protocol and execution | 16–32+ hours | Approved data, environment, and evaluation authority |
| Trusted artifact build and release evidence | 8–16 hours | Approved inputs, trust root, and reviewer |
| Security/privacy/operations and deployment review | 8–20 hours | Reviewers and deployment owner |

The total project timeline cannot be responsibly estimated until owner decisions, rights evidence, package-source approval, artifact trust, and release authorization are available. No waiting-time estimate is assigned to those external dependencies.

## Checks performed

- `git rev-parse HEAD` — returned `8c41ae005f4bee178a2b0104cb29049f00182081`.
- `git status --short` — recorded the pre-existing tracked and untracked changes listed by Git.
- `Test-Path` checks — all five required reports exist.
- `rg` inspection — confirmed blocker statuses, pending decisions, safe-work boundaries, smoke-test surfaces, and Task 63’s FND-LRIL hold.
- `git diff --check` — completed without errors; existing line-ending warnings were reported by Git.
- Final HEAD and status were rechecked after creating this report.

No application tests were run because this task is an audit and task-selection exercise; no test result is being claimed.

## Restricted activities not performed

No datasets or article rows were downloaded, acquired, or inspected. No models or serialized artifacts were loaded. No training, calibration, evaluation, inference, package installation, external contact, deployment, commit, push, tag, reset, clean, stash, or destructive Git operation occurred. Track A behavior, Track B production isolation, release gates, and the public `NO-GO` status were not changed.

## Final recommendation

Proceed next with the bounded model-free application security/privacy readiness slice described above. Do not begin dataset-dependent, artifact-dependent, or release-dependent work until the owner completes the pending decision gates. Stop after that next task and reassess only from its actual evidence.
