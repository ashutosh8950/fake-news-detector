# Task 68 — Security Header Policy and Operational Endpoint Exposure Controls

**Date:** 2026-10-27  
**Release posture:** `NO-GO` for public Fake/Real inference

## Summary

This task added a small application-level security-header policy and made `/metrics` fail closed unless deployment configuration supplies an explicit bearer-token secret. `/docs`, `/openapi.json`, and `/health` remain available for local diagnosis; their public exposure in a hosted deployment remains an owner/deployment decision. TLS, HSTS, proxy behavior, log retention, and distributed abuse controls remain outside what the repository can prove.

## Files inspected

- `evaluation_results/new_release_candidate_2026-10-22/task67_deployment_security_audit/TASK67_DEPLOYMENT_SECURITY_AUDIT.md`
- `evaluation_results/new_release_candidate_2026-10-22/task65_model_free_security_privacy_review/TASK65_MODEL_FREE_SECURITY_PRIVACY_REVIEW.md`
- `evaluation_results/new_release_candidate_2026-10-22/task66_browser_history_privacy_fix/TASK66_BROWSER_HISTORY_PRIVACY_FIX.md`
- `evaluation_results/new_release_candidate_2026-10-22/task57_release_blocker_register/TASK57_RELEASE_BLOCKER_REGISTER.md`
- `app.py`, `routers/api.py`, `config.py`, `frontend/app.js`, `frontend/index.html`
- `render.yaml`, `Dockerfile`, `requirements.txt`, `.github/workflows/ci.yml`
- Existing model-free tests and `scripts/run_safe_local_verification.ps1`

## Changes made

### `app.py`

Added middleware that applies these headers to UI and API responses:

- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `Referrer-Policy: no-referrer`
- `Permissions-Policy: camera=(), microphone=(), geolocation=()`

No CSP was added. The current UI uses inline JavaScript/style behavior and external font resources; a compatible CSP requires an explicit design and deployment decision rather than a blind restrictive header. HSTS was also not added because the application serves local HTTP during development and TLS termination belongs to the eventual hosting layer.

### `routers/api.py`

`GET /metrics` now has this fail-closed policy:

- If `METRICS_ACCESS_TOKEN` is not configured, return HTTP 404 without metrics.
- If configured, require `Authorization: Bearer <token>` and compare it using constant-time comparison.
- Missing or incorrect credentials return HTTP 401 with `WWW-Authenticate: Bearer`.

This does not create credentials or expose the token. The deployment owner must provision and protect the secret before an authorized operator can use `/metrics`.

### `tests/test_security_headers_and_endpoints.py`

Added synthetic model-free tests covering the headers on `/`, `/health`, `/docs`, and `/openapi.json`, plus the default-deny and token-required `/metrics` behavior.

No Track A prediction behavior, model readiness logic, Track B routing, dependency file, or deployment file was changed.

## Endpoint exposure policy

| Endpoint | Local behavior | Hosted deployment policy | Status |
|---|---|---|---|
| `/health` | Available and reports readiness; unavailable models produce 503 and `models_loaded: false` | May be public if the hosting owner accepts the limited readiness disclosure | Requires owner/deployment approval |
| `/docs` | Available for local diagnosis | Prefer restricted access or disable in a public production deployment unless intentionally documented | Pending deployment decision |
| `/openapi.json` | Available as part of FastAPI documentation | Same policy as `/docs`; public schema exposure must be intentional | Pending deployment decision |
| `/metrics` | 404 by default; bearer token required when enabled | Keep disabled unless a protected secret and access path are approved | Application default implemented; deployment secret/policy pending |
| `/models/info` | 503 when trusted artifacts are unavailable; otherwise exposes model metadata | Restrict or review before public exposure because it may disclose model metadata | Pending deployment decision |
| `/analyze` and `/analyze/deep` | Remain guarded by readiness checks and rate limits | Do not enable public inference until all release gates are cleared | `NO-GO` |

## Confirmed versus unverified findings

### Confirmed

- The new headers are applied by application middleware and are asserted by tests.
- `/metrics` is not publicly usable by default after this change.
- A configured bearer token is required for metrics access; wrong and missing credentials fail with 401.
- `/health` remains fail-closed for unavailable trusted artifacts.
- Existing Task 66 content-retention fix remains present.
- Track B remains outside production routing.

### Unverified deployment assumptions

- Whether Render, Docker ingress, or another eventual proxy terminates TLS correctly.
- Certificate renewal, HSTS policy, forwarded-client-IP handling, and proxy trust configuration.
- Whether `/docs`, `/openapi.json`, `/models/info`, or `/health` are restricted by the hosting platform.
- Secret provisioning, rotation, access logging, and incident response for `METRICS_ACCESS_TOKEN`.
- Application/server log retention and redaction.
- Distributed rate limiting and concurrency/resource quotas.
- A compatible CSP for the current frontend and any external font policy.

## Tests executed

Focused command:

```powershell
.\\.venv\\Scripts\\python.exe -m pytest tests/test_security_headers_and_endpoints.py tests/test_frontend_privacy.py tests/test_frontend_response_contract.py tests/test_application_e2e.py tests/test_readiness_contract.py tests/smoke/test_local_readiness_smoke.py tests/test_api.py -q
```

Result: **35 passed, 2 warnings in 6.26 seconds**.

Approved safe runner:

```powershell
.\\scripts\\run_safe_local_verification.ps1
```

Result:

- Model-free readiness smoke tests: **4 passed, 2 warnings**.
- Synthetic Track B regression tests: **20 passed**.
- Final result: `SAFE LOCAL VERIFICATION PASSED`.

Warnings were existing FastAPI/Starlette/httpx and AnyIO deprecation warnings. Tests used synthetic inputs and patched unavailable-model startup paths. No model artifacts, datasets, article rows, external services, or browser were accessed.

Validation:

- `git diff --check` completed without errors; existing LF/CRLF conversion warnings were reported for pre-existing modified files.
- No deployment was started and no hosting platform was contacted.

## Owner decisions still required

1. Approve the intended public exposure of `/health`, `/docs`, `/openapi.json`, and `/models/info`.
2. Approve the operational owner and secret-management path for `METRICS_ACCESS_TOKEN`, or keep `/metrics` disabled.
3. Approve a CSP compatible with the frontend, including whether external fonts are allowed.
4. Define TLS/HSTS, proxy, logging, retention, monitoring, and abuse-response requirements for the eventual host.
5. Resolve dataset rights/provenance, trusted artifact provenance, dependency reproducibility, authorized evaluation, and final release approval before enabling inference.

## Git and safety state

- HEAD before and after: `8c41ae005f4bee178a2b0104cb29049f00182081`.
- Initial working-tree status was recorded before editing and contained extensive pre-existing tracked modifications and untracked project/report files.
- Final status was rechecked after validation. The new Task 68 work consists of the changes to `app.py`, `routers/api.py`, `tests/test_security_headers_and_endpoints.py`, and this report; all prior changes were preserved.
- No files were reset, deleted, committed, pushed, tagged, or deployed.

## Restricted activities

No dataset acquisition or article-row inspection occurred. No model or serialized artifact was loaded. No training, calibration, evaluation, inference, package installation, external contact, deployment, publication, or release-gate change occurred. Public release remains `NO-GO`.

## Effort estimates

Next task: approximately **4–8 agent-hours** for a deployment-owner-approved proxy/TLS, log-retention, and operational-endpoint review, excluding external configuration and security review. Remaining engineering effort before a defensible public release is approximately **35–75+ agent-hours after** rights, artifact, dependency, evaluation, scope, and authorization gates are cleared. External waiting time remains unknown.
