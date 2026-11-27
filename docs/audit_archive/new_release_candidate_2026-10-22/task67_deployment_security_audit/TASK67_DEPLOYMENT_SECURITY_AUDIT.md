# Task 67 — Deployment Security and Privacy Controls Audit

**Audit date:** 2026-10-27  
**Release posture:** `NO-GO` for public Fake/Real inference

## Scope and evidence classification

This was a repository inspection plus model-free regression run. “Confirmed” means visible in the inspected source or exercised by the listed tests. “Potential” means a risk follows from the source but deployment behavior is not established. “Unverified” means the repository does not provide evidence for the control. No hosting platform was accessed.

## Files and configurations inspected

- `evaluation_results/new_release_candidate_2026-10-22/task64_safe_next_task_audit/TASK64_SAFE_NEXT_TASK_AUDIT.md`
- `evaluation_results/new_release_candidate_2026-10-22/task65_model_free_security_privacy_review/TASK65_MODEL_FREE_SECURITY_PRIVACY_REVIEW.md`
- `evaluation_results/new_release_candidate_2026-10-22/task66_browser_history_privacy_fix/TASK66_BROWSER_HISTORY_PRIVACY_FIX.md`
- `evaluation_results/new_release_candidate_2026-10-22/task57_release_blocker_register/TASK57_RELEASE_BLOCKER_REGISTER.md`
- `evaluation_results/new_release_candidate_2026-10-22/task57_release_blocker_register/TASK57_OWNER_DECISION_AND_CRITICAL_PATH.md`
- `app.py`, `routers/api.py`, `config.py`, `frontend/app.js`, `frontend/index.html`
- `render.yaml`, `Dockerfile`, `requirements.txt`, `.github/workflows/ci.yml`
- `tests/test_frontend_privacy.py`, `tests/test_frontend_response_contract.py`, `tests/test_application_e2e.py`, `tests/test_readiness_contract.py`, `tests/smoke/test_local_readiness_smoke.py`, `tests/test_api.py`
- `scripts/run_safe_local_verification.ps1` and `tests/smoke/README.md`

## Findings

### Confirmed controls

1. **Fail-closed model readiness — confirmed.** `app.py` catches startup model-load failures and leaves the application serving diagnostics. `routers/api.py` returns HTTP 503 from `/health` when `predictor.loaded` is false and rejects `/analyze` before calling prediction with `Inference unavailable: trusted model artifacts are not ready.` The model-free tests assert this behavior and assert that prediction is not called.

2. **Basic request limits — confirmed.** `AnalyzeRequest` limits article text to 10,000 characters and title to 500 characters, strips whitespace, and rejects text shorter than 20 characters. `/analyze` is limited to 10 requests/minute and `/analyze/deep` to 5 requests/minute through SlowAPI. The 429 handler returns a bounded JSON message and preserves retry headers where available.

3. **Frontend failure handling and Task 66 privacy fix — confirmed for tested source paths.** `frontend/app.js` hides the result area on `showError`, writes error text with `textContent`, restores busy state in `finally`, validates responses before rendering, and no longer persists article/title content in `truthscan.history`. The Task 66 regression checks passed as part of the command below.

4. **Track separation — confirmed by inspection and existing test.** `app.py` includes only `routers.api`; no production route imports the synthetic Track B API, and the application OpenAPI path set is checked by `tests/test_application_e2e.py` to exclude `/claim`.

5. **Bounded server error responses — confirmed for inspected handlers.** The global exception handler returns a generic 500 message with a request ID rather than a traceback. Route-level prediction errors return a generic analysis failure message. This does not establish the privacy of the server’s log sink.

### Potential risks

1. **Operational logs may retain more information than intended.** `routers/api.py` logs input length, predicted label, confidence, and processing time, while `app.py` logs exception details with `logger.exception` and logs model metadata at startup. The article body is not included in the inspected normal log messages, but the production sink, access-log behavior, retention, access controls, and redaction policy are not configured in the repository. This is a deployment-dependent potential risk.

2. **Rate limiting may not be effective across a deployed topology.** SlowAPI is configured with an in-process limiter keyed by remote address. No shared limiter store, worker coordination, trusted proxy configuration, or abuse-response procedure is present in the inspected files. Render and Docker both start one worker as configured, but that does not establish protection across restarts, replicas, proxy address handling, or distributed traffic.

3. **`/metrics` is unauthenticated in application code.** `routers/api.py` exposes request totals, Fake/Real counts, average confidence, uptime, and model readiness at `GET /metrics`; no authentication or authorization is visible. Whether the hosting platform restricts this route is unknown. Public exposure should be an explicit deployment decision.

4. **Deployment build steps retrieve external resources.** `render.yaml` runs `python -m spacy download en_core_web_sm` and `python download_models.py`; `Dockerfile` likewise downloads the spaCy model and runs `download_models.py` during image build. This audit did not execute either path. Their source, artifact provenance, package source, and release policy remain separate blockers and should not be treated as verified by this report.

5. **CORS is configuration-sensitive.** `app.py` defaults to the named production origin and permits `ALLOWED_ORIGINS` to override it. No wildcard is present in the inspected default, but the actual deployment environment variable and ownership of that configuration were not verified.

### Unverified or missing controls

- HTTPS/TLS termination, HSTS, certificate management, and forwarded-header/proxy configuration.
- Content Security Policy, frame protection, referrer policy, and `X-Content-Type-Options` or equivalent security headers. No explicit security-header middleware was found in `app.py`.
- Production access-log and application-log retention, redaction, access control, and deletion.
- Distributed rate limiting, concurrency quotas, request timeouts, body-size enforcement at the proxy, and abuse escalation.
- Authentication or network policy for `/metrics`, `/docs`, and OpenAPI exposure.
- Monitoring, alerting, incident response, privacy notice, consent, and deletion procedures.
- Whether deployment uses the repository’s declared single-worker configuration or another topology.

These are evidence gaps, not claims about controls that may exist outside the repository.

## Privacy regression validation

Task 66’s implementation was inspected. It removes only `truthscan.history`, starts history as an in-memory session array, stores aggregate statistics separately, and renders generic session text. It does not claim to remove old data from browser backups, profiles, synchronized storage, screenshots, server logs, or other devices. The focused privacy tests passed.

## Tests executed

Command:

```powershell
.\\.venv\\Scripts\\python.exe -m pytest tests/test_frontend_privacy.py tests/test_frontend_response_contract.py tests/test_application_e2e.py tests/test_readiness_contract.py tests/smoke/test_local_readiness_smoke.py tests/test_api.py -q
```

Actual result: **32 passed, 2 warnings in 4.82 seconds**.

The warnings were existing FastAPI/Starlette/httpx and AnyIO deprecation warnings. The tests use synthetic inputs and patched unavailable-model startup paths; no model artifacts, dataset rows, real inference, browser, deployment, or external service was used.

Additional check:

- `git diff --check` completed without errors. Git emitted existing LF/CRLF conversion warnings for pre-existing modified files.

## Safe fixes applied

None in this task. The identified deployment gaps require deployment-owner/security decisions or hosting-platform configuration and cannot be safely resolved by changing application code without scope approval. The Task 66 frontend privacy change was pre-existing work and was preserved, not reimplemented here.

## Release blockers and recommended next step

Public release remains `NO-GO` because dataset/article rights and provenance, trusted model-artifact provenance, reproducible dependencies, authorized evaluation, deployment privacy/security controls, owner scope decisions, and final release authorization remain unresolved. The historical `production_switch` metadata conflict also remains documented elsewhere and was not changed.

The next smallest implementation task is a model-free deployment-hardening slice: define and test an explicit security-header policy and make the exposure policy for `/metrics` and `/docs` explicit, using a deployment-owner-approved configuration. This should be followed by a separate review of proxy/TLS, log retention, and distributed abuse controls. Do not enable inference as part of that work.

## Git and safety state

- HEAD before and after inspection: `8c41ae005f4bee178a2b0104cb29049f00182081`.
- Initial working-tree status was recorded before inspection and contained extensive pre-existing tracked modifications and untracked reports/files.
- The final status was rechecked after creating this report. The only new Task 67 artifact is this report under the existing untracked `evaluation_results/new_release_candidate_2026-10-22/` tree; prior changes were preserved.
- No production source, deployment configuration, model artifact, dataset, dependency lock, or release gate was modified by this task.

## Restricted activities

No dataset acquisition or article-row inspection occurred. No model or serialized artifact was loaded. No training, calibration, evaluation, inference, package installation, external contact, deployment, publication, commit, push, tag, reset, clean, stash, or destructive operation occurred.

## Effort estimates

The next bounded deployment-hardening task is approximately **4–8 agent-hours**, excluding deployment-owner/security review and hosting-platform changes. Remaining engineering effort before a defensible public release is approximately **35–75+ agent-hours after** rights, artifact trust, dependency, evaluation, scope, and authorization gates are cleared. External waiting time is unknown and excluded.
