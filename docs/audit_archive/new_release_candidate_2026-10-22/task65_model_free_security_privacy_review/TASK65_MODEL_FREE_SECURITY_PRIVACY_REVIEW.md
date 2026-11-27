# Task 65 — Model-Free Application Security and Privacy Readiness Review

**Review date:** 2026-10-27  
**Scope:** model-free static inspection and synthetic regression tests  
**Release posture:** `NO-GO` for public Fake/Real inference

## Executive summary

The current application has useful fail-closed and boundary protections. The API validates article length before inference, returns controlled unavailable-model responses, applies endpoint rate limits, and does not import the synthetic Track B API. The focused model-free suite passed 24 tests with 2 existing dependency deprecation warnings.

One confirmed privacy risk remains: after a successful analysis, the frontend stores a 120-character excerpt of the submitted title/article in browser `localStorage` under `truthscan.history`. The repository does not define a retention period, sensitive-content policy, browser-storage threat model, or automatic deletion behavior. This was not changed because the safe remedy requires an owner decision about whether local history is permitted and what retention policy applies.

Other controls—production log retention, TLS/proxy behavior, distributed rate limiting, operational monitoring, CSP/security headers, and deployment privacy configuration—could not be established from the inspected repository. They remain release gaps, not confirmed vulnerabilities.

## Files inspected

### Prior readiness and blocker records

- `evaluation_results/new_release_candidate_2026-10-22/task64_safe_next_task_audit/TASK64_SAFE_NEXT_TASK_AUDIT.md`
- `evaluation_results/new_release_candidate_2026-10-22/task57_release_blocker_register/TASK57_RELEASE_BLOCKER_REGISTER.md`
- `evaluation_results/new_release_candidate_2026-10-22/task57_release_blocker_register/TASK57_OWNER_DECISION_AND_CRITICAL_PATH.md`
- `evaluation_results/new_release_candidate_2026-10-22/task59_owner_decision_checkpoint/TASK59_OWNER_DECISION_CHECKPOINT.md`

### Application and test files

- `app.py`
- `routers/api.py`
- `predictor.py`
- `config.py`
- `frontend/app.js`
- `frontend/response_contract.js`
- `frontend/index.html`
- `frontend/style.css`
- `tests/test_api.py`
- `tests/test_readiness_contract.py`
- `tests/test_application_e2e.py`
- `tests/test_frontend_response_contract.py`
- `tests/smoke/test_local_readiness_smoke.py`
- `scripts/run_safe_local_verification.ps1`

No dataset rows, article collections, model artifacts, or serialized model contents were inspected.

## Confirmed findings

### C-01 — Input length and shape validation occurs before inference

**Evidence:** `routers/api.py`, `AnalyzeRequest`.

- `text` is required and has `max_length=10000`.
- `title` is optional and has `max_length=500`.
- Whitespace is stripped before validation.
- Article text shorter than 20 characters is rejected.
- FastAPI/Pydantic rejects malformed JSON and wrong field types before the route reaches `predictor.predict`.
- The `/analyze` and `/analyze/deep` routes check model readiness before entering inference.

**Assessment:** Confirmed from source and exercised by the model-free tests for missing/short input and unavailable models. This is a bounded request-control safeguard, not proof that all deployment-level resource exhaustion risks are solved.

### C-02 — Unavailable trusted artifacts fail closed

**Evidence:** `app.py` lifespan and `routers/api.py` routes `/health`, `/analyze`, `/models/info`, and `/analyze/deep`; `predictor.py`.

- Startup catches model-load failures, sets `predictor.loaded = False`, and keeps health/documentation serving.
- `/health` returns HTTP 503 with `status: not_ready` and `models_loaded: false` when the ensemble is unavailable.
- `/analyze` returns HTTP 503 with `Inference unavailable: trusted model artifacts are not ready.` before calling prediction.
- `predictor.py` verifies the artifact bundle before deserializing joblib objects, but no artifact was loaded in this review.

**Assessment:** Confirmed by source inspection and tests. The current behavior was not weakened.

### C-03 — Client-facing unexpected failures are bounded

**Evidence:** `app.py` global exception handler; `routers/api.py` inference exception branches; `frontend/app.js`.

- The global handler returns a generic 500 message and a request ID rather than a traceback.
- Route-level inference failures return `Analysis failed, please try again`.
- Frontend errors use text rendering through `textContent` for the error message.
- Malformed response data is rejected by `TruthScanResponseContract` before result rendering.

**Assessment:** Confirmed for the inspected code paths and model-free tests. Server logs still contain exception details, so the production log sink and access policy must be reviewed separately.

### C-04 — Track B remains outside production routing

**Evidence:** `app.py` imports only `routers.api`; production source search found no import of `synthetic_claim_api` or `synthetic_evidence_demo`. `tests/test_application_e2e.py` asserts that no `/claim` route exists and no Track B module is imported.

**Assessment:** Confirmed by source inspection and the focused test suite. The isolated prototype remains under `evaluation_results/.../task44_synthetic_prototype/` and is not mounted by the FastAPI app.

### C-05 — Basic request throttling exists

**Evidence:** `routers/api.py` applies `slowapi` limits of `10/minute` to `/analyze` and `5/minute` to `/analyze/deep`; `app.py` installs `SlowAPIMiddleware` and returns a structured 429 response.

**Assessment:** Confirmed as application-level code. Its suitability for multiple workers, reverse proxies, NAT/shared IPs, or hostile distributed traffic is unverified.

## Confirmed privacy risk

### P-01 — Submitted content is retained in browser local storage after successful analysis

**Evidence:** `frontend/app.js`, `recordAnalysis()` and storage initialization.

```text
recordAnalysis(result, title || text)
...
snippet: snippetSource.slice(0, 120)
saveJSON(STORAGE.history, state.history)
```

The state is loaded from `localStorage` key `truthscan.history`, and the UI renders the saved snippet in the Recent Analyses list. The clear-history action deletes the current stored history, but there is no automatic expiry, tab/session boundary, encryption, consent prompt, sensitive-content warning, or documented retention period in the inspected repository.

**Severity:** Medium for a local portfolio application; potentially high for a public service receiving confidential, personal, legal, medical, or unpublished text. Severity depends on intended use and deployment context.

**Why no fix was applied:** Removing history, retaining only non-content metadata, or adding expiry would each be a product/privacy decision. The owner must decide whether local history is allowed and what data-retention policy applies before changing the behavior. A future fix should be minimal and tested, and should not claim that browser local storage is suitable for public-submission privacy by default.

## Potential risks requiring follow-up

### R-01 — Server log retention and access are not documented

`routers/api.py` logs article length, predicted label, confidence, and processing time. It does not log the article body in the inspected messages. However, exception logging in `app.py` and route-level error logging may capture exception details, and the repository does not define the production sink, retention period, access controls, redaction policy, or whether upstream server/access logs include request bodies.

**Status:** Potential risk; operational behavior unverified.

### R-02 — Rate limiting is likely process-local unless deployment supplies shared state

The code uses `slowapi.Limiter` with the client address as the key. No distributed store, worker coordination, proxy configuration, or abuse-response policy was found in the inspected files.

**Status:** Implemented local control; deployment-level effectiveness unverified.

### R-03 — CORS is configurable and requires deployment review

`app.py` uses a production-origin default and allows `ALLOWED_ORIGINS` to override it. The repository does not establish who controls production environment variables or whether deployment values are reviewed. No wildcard origin was found in the inspected source, but configuration-level misuse remains possible.

**Status:** Source safeguard partially verified; deployed configuration unverified.

### R-04 — Security headers and transport protections are not established

The inspected FastAPI setup does not show explicit CSP, HSTS, frame, referrer, or content-type security headers. TLS termination may occur outside the repository, but this was not verified.

**Status:** Unverified control; requires deployment/security review.

### R-05 — Metrics expose aggregate operational information

`/metrics` returns request totals, Fake/Real counts, average confidence, uptime, and model readiness. No authentication or authorization is visible in the route. The sensitivity of these aggregates and whether the endpoint is public in deployment are not documented.

**Status:** Potential information-disclosure risk; deployment exposure unverified.

## Unverified controls

The following cannot be marked implemented from the repository alone:

- explicit privacy notice and consent for submitted content;
- automatic retention/deletion policy for browser and server data;
- production log redaction, access control, and retention;
- TLS, reverse-proxy, and forwarded-client-IP configuration;
- distributed rate limiting and concurrency/resource quotas;
- authentication or access policy for `/metrics` and `/docs`;
- production monitoring, alerting, incident response, and abuse handling;
- Content Security Policy and other response security headers;
- owner-approved public deployment configuration;
- legal/rights clearance for visitor-submitted content or model training data.

These are not claims that the controls are absent everywhere; they are evidence gaps in the inspected repository.

## Tests executed

Command executed with the existing virtual environment:

```powershell
.\.venv\Scripts\python.exe -m pytest tests/test_readiness_contract.py tests/smoke/test_local_readiness_smoke.py tests/test_frontend_response_contract.py tests/test_api.py -q
```

Result:

```text
24 passed, 2 warnings in 11.21s
```

Warnings were existing dependency deprecation warnings from FastAPI/Starlette/httpx compatibility. No test loaded a model artifact or accessed dataset rows; the smoke fixtures patch model and preprocessing startup paths and assert fail-closed behavior.

Additional checks:

- Static search confirmed no production import of `synthetic_claim_api`, `synthetic_evidence_demo`, or a `/claim` route.
- `git diff --check` completed without errors; Git reported existing LF/CRLF conversion warnings for pre-existing modified files.
- No browser automation was run.
- No production server was started.

## Fixes made

None. The confirmed local-storage retention risk requires a policy decision, and no production behavior was changed during this review.

## Remaining blockers and recommended follow-up

The Task 57 blockers remain active: dataset/article rights and provenance, trusted model-artifact authenticity, reproducible dependencies, authorized leakage-aware evaluation, the `production_switch` ambiguity, operational security/privacy/abuse controls, and final release authorization. Task 63 also remains pending for the FND-LRIL continuation decision.

Recommended next implementation task: obtain an owner decision on browser-history retention, then make the smallest privacy-safe frontend change—preferably no content retention by default or an explicitly bounded, user-controlled local history—followed by focused tests. Separately, a deployment-owner review is required for log handling, security headers, `/metrics` exposure, proxy behavior, and distributed rate limiting.

## Effort estimates

Approximate planning estimates only:

- Next task: 2–4 agent-hours after the owner chooses a retention policy, including implementation and focused tests.
- Remaining engineering work before a defensible public release: approximately 40–80+ agent-hours after rights, data, artifact, dependency, evaluation, and scope gates are cleared.
- External waiting time for rights responses, qualified review, package-source approval, trust-root provisioning, owner decisions, and deployment authorization is unknown and excluded.

## Git and safety state

- HEAD before and after: `8c41ae005f4bee178a2b0104cb29049f00182081`.
- Working-tree status was recorded before and after; the existing status count remained 47 entries.
- No existing tracked modification or untracked file was overwritten or removed.
- No dataset or article content was acquired or inspected.
- No model or serialized artifact was loaded.
- No training, calibration, evaluation, inference, package installation, external contact, deployment, commit, push, tag, or destructive Git operation occurred.
- Public release remains `NO-GO`.
