# Task 70 — CSP Report-Only Compatibility and Deployment Security Decision Register

**Review date:** 2026-10-27  
**Executive verdict:** `PASS WITH FOLLOW-UP`  
**Release posture:** `NO-GO` for public Fake/Real inference

This was a read-only compatibility assessment. No application code, production configuration, tests, dependencies, existing reports, or Git history were changed. No CSP was activated and no reporting endpoint was added.

## Baseline and evidence classification

HEAD before review: `8c41ae005f4bee178a2b0104cb29049f00182081`. The initial working tree contained extensive pre-existing tracked modifications and untracked project/report files; these were preserved. Findings below are independently reproduced from the listed files or test command unless explicitly described as an assumption or deployment gap.

## Files and locations reviewed

- `evaluation_results/new_release_candidate_2026-10-22/task69_csp_docs_exposure_review/TASK69_CSP_DOCS_EXPOSURE_REVIEW.md`
- `evaluation_results/new_release_candidate_2026-10-22/task68_security_headers_endpoint_policy/TASK68_SECURITY_HEADERS_ENDPOINT_POLICY.md`
- `app.py:78-103, 138-177` — FastAPI construction, global error handling, security headers, CORS, route mounting
- `routers/api.py:20, 57-109` — readiness, metrics-token gate, and operational endpoints
- `frontend/index.html:8-11, 73-103, 188-192, 237, 296-297` — fonts, inline styles/SVG, local scripts
- `frontend/app.js:216-267, 297-426, 473-520` — fetch calls, dynamic HTML, validation, error/result rendering, session history
- `frontend/style.css`
- `frontend/response_contract.js`
- `render.yaml`, `Dockerfile`, `.github/workflows/ci.yml`
- `tests/test_security_headers_and_endpoints.py`, `tests/test_application_e2e.py`, `tests/test_frontend_privacy.py`, `tests/test_frontend_response_contract.py`, `tests/test_readiness_contract.py`, `tests/smoke/test_local_readiness_smoke.py`

## Confirmed findings

### CSP status and compatibility

- No `Content-Security-Policy` or `Content-Security-Policy-Report-Only` header or directive was found in repository code or deployment files inspected.
- The application already applies non-CSP headers in `app.py:88-103`: `nosniff`, `X-Frame-Options: DENY`, `Referrer-Policy: no-referrer`, and a restrictive `Permissions-Policy`.
- `frontend/index.html` loads two same-origin scripts, `/static/style.css`, and Google Fonts from `fonts.googleapis.com`/`fonts.gstatic.com`.
- The page contains inline `style` attributes and inline SVG style attributes. `frontend/app.js` also generates HTML containing inline style attributes for animations.
- The page has no inline `<script>` block in the inspected markup; its scripts are external same-origin files.
- `frontend/app.js` uses `innerHTML` for controlled UI templates. CSP would not sanitize those sinks; response validation and escaping remain necessary.

### Documentation and operational endpoints

- `FastAPI(...)` in `app.py:78-83` does not set `docs_url`, `redoc_url`, or `openapi_url` to `None`; `/docs`, `/redoc`, and `/openapi.json` are therefore enabled by default.
- No route-level authentication for documentation or `/models/info` was found.
- `/health` is intended to remain available for readiness diagnosis and reports model readiness state.
- `/metrics` is fail-closed after Task 68: absent token configuration returns 404; configured deployments require a bearer token.
- Hosting-layer restrictions for these endpoints were not inspected and cannot be inferred from the repository.

### Metrics-token handling

`routers/api.py:20, 83-105` reads `METRICS_ACCESS_TOKEN` without printing it. Missing configuration is denied by default. Authorization parsing requires the `Bearer` scheme and a non-empty value; comparison uses `secrets.compare_digest`. Error responses do not include the configured value. The tests use only synthetic token values. No explicit log statement includes the authorization header or token.

### Logging/privacy

- Normal analysis logs contain article length, label, confidence, and processing time (`routers/api.py:132-143` and `:160-165`), not the request body.
- The global exception handler logs exception details and returns a bounded message with a request ID (`app.py:140-151`).
- No application-level request-body or authorization-header logging was observed.
- Production access logs, proxy logs, crash reporting, retention, redaction, access permissions, and deletion behavior remain unverified.

## CSP resource inventory

| Resource/behavior | Observed evidence | Compatibility consequence |
|---|---|---|
| Same-origin scripts | `/static/response_contract.js`, `/static/app.js` | `script-src 'self'` is a plausible starting point; no inline script allowance is needed for the inspected HTML |
| Same-origin CSS | `/static/style.css` | `style-src 'self'` is required |
| Google Fonts CSS | `https://fonts.googleapis.com` stylesheet | Must be allowed in `style-src`, or fonts should be self-hosted |
| Google Fonts files | `https://fonts.gstatic.com` | Must be allowed in `font-src` if external fonts remain |
| Inline style attributes | Multiple `style="..."` attributes in HTML and generated markup | A strict style policy would block these; refactor to classes/controlled CSS variables or temporarily allow inline styles in report-only testing |
| Inline SVG styling | `frontend/index.html:188-192` | Must be tested under the chosen style policy; refactoring may be needed |
| Dynamic HTML | `innerHTML` in `frontend/app.js` | CSP does not replace output encoding or contract validation; continue escaping untrusted values and consider DOM APIs |
| API calls | `fetch()` to same-origin health, model-info, and analysis paths | `connect-src 'self'` is sufficient for same-origin deployment; cross-origin hosting would require an explicit origin |
| Images/data | No external image source was observed in the inspected markup | `img-src 'self' data:` is a conservative starting point if inline/data assets are retained |

## Proposed report-only policy

This is a candidate for controlled staging only; it was not added to the application:

```text
default-src 'self';
base-uri 'self';
object-src 'none';
frame-ancestors 'none';
script-src 'self';
style-src 'self' 'unsafe-inline' https://fonts.googleapis.com;
font-src 'self' https://fonts.gstatic.com data:;
img-src 'self' data:;
connect-src 'self';
form-action 'self'
```

The temporary `'unsafe-inline'` style allowance reflects the current inline styles and should not be treated as the desired final policy. No `'unsafe-eval'` or wildcard source is proposed. Once inline styles are refactored and font hosting is decided, tighten `style-src` and `font-src` accordingly. `upgrade-insecure-requests` and HSTS are intentionally omitted from this local HTTP-compatible proposal; they belong to the HTTPS deployment layer.

### Controlled report-only testing plan

1. Obtain owner/deployment approval for a staging-only report-only header and a controlled violation collector.
2. Add the header at the staging proxy or application boundary without adding a public collector to this repository.
3. Collect only CSP report metadata such as blocked directive/source and page path; redact query strings, authorization information, user identifiers, and any submitted-content fields before retention.
4. Exercise the homepage, unavailable-model state, validation error, API-offline behavior, model-info unavailable state, charts/history, docs navigation, and theme changes in a supported browser.
5. Review violations, refactor inline styles or approve a nonce/hash strategy, and repeat until expected resources are clean.
6. Enforce only after browser evidence and deployment-owner approval. This review did not perform browser or staging testing, so it does not establish compatibility.

## Documentation endpoint recommendations

| Endpoint | Development recommendation | Production recommendation | Evidence status |
|---|---|---|---|
| `/docs`, `/redoc`, `/openapi.json` | Keep available for local diagnosis | Restrict by network/authentication or disable intentionally; hiding a route is not authorization | Application defaults independently inspected; hosting unknown |
| `/models/info` | Keep available when debugging readiness | Restrict or remove from public surface because ready-state metadata may disclose model details | Application behavior inspected; hosting unknown |
| `/health` | Keep available for local and orchestrator checks | Public only if limited readiness disclosure is approved; otherwise use a separately scoped probe | Fail-closed behavior tested; deployment policy unknown |
| `/metrics` | Keep disabled unless a synthetic/local token is explicitly configured | Keep disabled unless secret provisioning, operator access, rotation, and monitoring are approved | Default-deny/token gate tested |

Documentation exposure does not authorize inference, establish model provenance, or replace authentication and authorization.

## Deployment-security decision register

| Decision/evidence required | Owner or source | Current status | Dependency/risk |
|---|---|---|---|
| HTTP is redirected to HTTPS and TLS terminates with managed certificates | Hosting/deployment owner and platform configuration | Unverified | Required before public submission; proxy misconfiguration can expose text in transit |
| HSTS is applied only after HTTPS is stable, with an approved scope | Deployment owner | Unverified | Incorrect preload/subdomain scope can affect unrelated hosts |
| Forwarded headers and client IP are trusted only from the approved proxy | Deployment owner | Unverified | Incorrect trust can undermine rate limits and auditability |
| Security headers are preserved and not overwritten by the proxy | Deployment owner/staging response inspection | Unverified | Proxy overrides could remove application protections |
| `/metrics` token is provisioned in a secret manager, rotated, never logged, and operator-only | Deployment owner | Pending owner decision | Token leakage exposes operational data |
| `/docs`, `/redoc`, `/openapi.json`, `/models/info` exposure is explicitly approved or restricted | Owner/deployment/security reviewer | Pending owner decision | Public schema/metadata may aid probing or disclose internals |
| Access/application logs have documented fields, redaction, retention, deletion, and access control | Deployment owner/privacy reviewer | Unverified | Platform logs may retain request metadata outside application control |
| CSP report collector is controlled, redacts sensitive fields, and has bounded retention | Deployment/security owner | Unverified | Reports can contain URL/path metadata and must not become a data-leak channel |
| Rate limits, body/time limits, worker topology, and abuse response are effective at the proxy and app layers | Deployment owner | Unverified | Process-local controls may not cover distributed deployments |

## Tests and commands actually run

Command:

```powershell
.\\.venv\\Scripts\\python.exe -m pytest tests/test_security_headers_and_endpoints.py tests/test_frontend_privacy.py tests/test_frontend_response_contract.py tests/test_application_e2e.py tests/test_readiness_contract.py tests/smoke/test_local_readiness_smoke.py -q
```

Observed result: **26 passed, 2 warnings in 7.58 seconds**. The warnings were existing FastAPI/Starlette/httpx and AnyIO deprecation warnings. The tests use synthetic inputs and patched unavailable-model startup paths; they do not load artifacts, access datasets, run real inference, or use the network.

`git diff --check` was run after report creation and completed without errors; the existing LF/CRLF conversion warnings were reported for pre-existing modified files. No browser-level or staging test was run.

## Prioritized next actions

1. Obtain an owner decision on production exposure of documentation, model metadata, health, and metrics endpoints.
2. Obtain controlled staging access and run the report-only CSP plan; do not enforce it yet.
3. Refactor inline styles or approve a nonce/hash strategy and decide whether to self-host fonts.
4. Verify TLS/HSTS, proxy trust, header preservation, and log retention with the deployment owner.
5. Keep public Fake/Real inference blocked until dataset rights, trusted artifact provenance, reproducible dependencies, authorized evaluation, privacy/security controls, and final release approval are complete.

## Final state and restrictions

- HEAD after review: `8c41ae005f4bee178a2b0104cb29049f00182081`, unchanged.
- Final working-tree status was rechecked; this Task 70 report is the only new artifact from this task under the existing untracked evaluation-results tree.
- No application code, production settings, tests, dependencies, or existing reports were modified.
- No CSP was activated, no reporting endpoint was added, and no operational endpoint was made more public.
- No datasets, article rows, models, packages, external services, training, calibration, evaluation, inference, deployment, commit, push, or tag operations occurred.
- Public release remains `NO-GO`.

## Effort estimates

Next task: approximately **4–8 agent-hours** for controlled staging CSP report-only testing and compatibility cleanup, excluding browser/staging access and security review. Remaining engineering effort before a defensible public release remains approximately **35–75+ agent-hours after** rights, artifact, dependency, evaluation, scope, and authorization gates are cleared. External waiting time is unknown.
