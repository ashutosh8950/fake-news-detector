# Task 69 — CSP Compatibility and API Documentation Exposure Review

**Review date:** 2026-10-27  
**Executive verdict:** `PASS WITH FOLLOW-UP`  
**Release posture:** `NO-GO` for public Fake/Real inference

This was a read-only review. No application, configuration, test, dependency, or existing report was edited. The only created file is this report.

## Baseline and files inspected

Git HEAD before review was `8c41ae005f4bee178a2b0104cb29049f00182081`. The working tree already contained extensive tracked modifications and untracked reports/files; they were preserved.

Inspected:

- `evaluation_results/new_release_candidate_2026-10-22/task67_deployment_security_audit/TASK67_DEPLOYMENT_SECURITY_AUDIT.md`
- `evaluation_results/new_release_candidate_2026-10-22/task68_security_headers_endpoint_policy/TASK68_SECURITY_HEADERS_ENDPOINT_POLICY.md`
- `evaluation_results/new_release_candidate_2026-10-22/task65_model_free_security_privacy_review/TASK65_MODEL_FREE_SECURITY_PRIVACY_REVIEW.md`
- `app.py`, `routers/api.py`, `config.py`
- `frontend/index.html`, `frontend/app.js`, `frontend/style.css`, `frontend/response_contract.js`
- `render.yaml`, `Dockerfile`, `.github/workflows/ci.yml`
- `tests/test_security_headers_and_endpoints.py`, `tests/test_application_e2e.py`, `tests/test_frontend_privacy.py`, `tests/test_frontend_response_contract.py`, `tests/test_readiness_contract.py`, `tests/smoke/test_local_readiness_smoke.py`

## Findings classification

### Confirmed

1. **Task 68 security headers are present in application middleware.** `app.py:88-103` applies `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `Referrer-Policy: no-referrer`, and a restrictive `Permissions-Policy` to responses. The existing Task 68 tests exercise `/`, `/health`, `/docs`, and `/openapi.json`.

2. **Metrics access is fail-closed in the inspected application.** `routers/api.py:20` reads `METRICS_ACCESS_TOKEN` without printing it. `metrics_endpoint()` returns 404 when it is absent and otherwise requires a bearer token, using `secrets.compare_digest`; missing or incorrect credentials return 401. The reviewed tests use only synthetic token values and do not expose a real secret.

3. **FastAPI documentation endpoints are enabled by default.** `app.py:78-83` constructs `FastAPI(...)` without `docs_url=None`, `redoc_url=None`, or `openapi_url=None`. Therefore `/docs`, `/redoc`, and `/openapi.json` are enabled unless a hosting layer restricts them. No route-level authentication was found for these endpoints.

4. **The UI is a mixed resource model that requires CSP planning.** `frontend/index.html:8-10` references Google Fonts; `:11` references `/static/style.css`; `:73`, `:83`, `:93`, `:103`, and other locations use inline `style` attributes; `:296-297` loads two local scripts. `frontend/app.js` creates dynamic HTML with `innerHTML` in model/result/chart/history rendering and uses inline style attributes in generated markup. User-controlled values observed in these templates are escaped or validated in the inspected paths, but CSP compatibility and DOM-safety are separate concerns.

5. **No CSP is currently configured in repository code.** A repository search found no `Content-Security-Policy` or `Content-Security-Policy-Report-Only` directive. Hosting behavior was not accessed, so an externally configured CSP cannot be ruled out.

6. **Task 66’s browser-history privacy fix remains present.** `frontend/app.js` removes only the legacy `truthscan.history` key and no longer persists article/title snippets. This review did not inspect browser profiles or deployed logs.

### Not observed in inspected source

- No authorization header or metrics token is logged by the explicit `app.py`/`routers/api.py` logging statements inspected.
- No article body is included in the normal analysis log messages; those messages log character count, label, confidence, and processing time.
- No explicit request-body logging, token logging, or article-body persistence was found in the inspected application code.
- No Track B import or production `/claim` route was observed in the reviewed application paths.

“Not observed” is not proof about platform access logs, web-server logs, crash reporting, browser extensions, or deployment configuration.

### Unverified

- Whether a hosting platform adds or removes headers.
- Whether TLS termination, HSTS, proxy trust, forwarded-client-IP behavior, and certificate management are configured securely.
- Whether `/docs`, `/redoc`, `/openapi.json`, `/models/info`, or `/health` are restricted by the hosting platform.
- Whether production log sinks retain request metadata, authorization headers, query strings, exception details, or body content.
- Whether a deployed CSP exists outside this repository.
- Secret provisioning, rotation, access control, and incident response for `METRICS_ACCESS_TOKEN`.

## CSP resource inventory

| Resource or behavior | Evidence | CSP implication |
|---|---|---|
| Local CSS | `/static/style.css` in `frontend/index.html:11` | `style-src` must allow the same-origin stylesheet |
| Local scripts | `/static/response_contract.js` and `/static/app.js` at `:296-297` | `script-src 'self'` can support these external scripts |
| Google Fonts connection | `preconnect` to `https://fonts.googleapis.com` and `https://fonts.gstatic.com` at `:8-10` | `connect-src`/`font-src`/`style-src` need explicit external-font allowances, or fonts should be self-hosted before tightening CSP |
| Inline style attributes | Multiple `style="..."` attributes in `index.html` and dynamically generated markup in `app.js` | A strict `style-src` without `'unsafe-inline'` would require refactoring to classes, CSS variables, or approved hashes/nonces; CSP style hashes do not generally solve all style-attribute cases without the appropriate CSP level/directive |
| Dynamic DOM HTML | `innerHTML` in `app.js:230,252,362,384,495,509-520` | A CSP does not itself sanitize HTML; retain escaping/contract validation and consider DOM construction APIs for untrusted values |
| Inline SVG attributes | Inline SVG in `index.html:188-192` uses style attributes | CSP compatibility must be tested with the chosen browser policy |
| External links | GitHub, Render, and Hugging Face links in `index.html:287-289` | Navigation policy should be decided separately; `rel="noopener"` is present on target-blank links |

## Proposed CSP policy and staged testing plan

No CSP was activated in Task 69. The safest next approach is:

1. **Inventory and refactor first.** Move inline style attributes and dynamic presentation styles into classes or controlled CSS variables where practical. Keep application data values out of HTML sinks unless they are validated and escaped.
2. **Start report-only.** Deploy a `Content-Security-Policy-Report-Only` policy in a controlled staging environment with a reporting destination owned by the operator. Do not send reports to an unapproved external service.
3. **Initial compatible policy shape.** A candidate policy could use same-origin resources for scripts/styles and explicitly list the chosen font source, while temporarily accommodating existing inline styles only if the owner accepts the trade-off. `object-src 'none'`, `base-uri 'self'`, and `frame-ancestors 'none'` are reasonable candidates, subject to UI testing. This is a design proposal, not an active configuration.
4. **Tighten iteratively.** Replace inline styles with classes/variables, decide whether to self-host fonts, remove unnecessary external links or constrain navigation, then remove any temporary inline allowances.
5. **Enforce only after evidence.** Test homepage, model-unavailable state, validation/error states, API docs navigation, and all dynamic result/history rendering in a real supported browser before enforcing the policy.

The trade-off is that a maximally restrictive policy may break the current visual design or font loading. Conversely, allowing broad inline execution would weaken the policy. A nonce/hash design would be appropriate only after the inline resources are identified and generated/managed reliably by the deployment process.

## API documentation and operational endpoint exposure

### Current application behavior

- `/docs`, `/redoc`, and `/openapi.json` are enabled by FastAPI defaults.
- `/health` is available and reports `models_loaded: false` with HTTP 503 when trusted artifacts are unavailable.
- `/models/info` returns 503 when models are unavailable, but could disclose model metadata when ready.
- `/metrics` is disabled by default at application level after Task 68 and requires a configured bearer token when enabled.
- The repository does not show authentication for documentation or model metadata endpoints.

### Recommended deployment policy

- Keep `/metrics` disabled unless an approved secret-management and operator-access path exists.
- Restrict `/docs`, `/redoc`, `/openapi.json`, and `/models/info` in a public deployment, or explicitly approve their exposure after reviewing the information they disclose. Hiding docs is not an authentication or authorization mechanism.
- Keep `/health` public only if the limited readiness disclosure is accepted by the deployment owner; otherwise provide a separately scoped health probe or network restriction.
- Do not treat endpoint obscurity as a substitute for authentication, network policy, rate limits, or release approval.

## Logging and privacy review

### Directly supported by code

- Normal analysis logs contain length, label, confidence, and processing-time metadata, not the article body (`routers/api.py:132-143` and `:160-165`).
- Errors are returned with bounded messages; the global handler emits a request ID and logs exception details (`app.py:140-151`).
- The metrics authorization token is not included in the inspected log statements.
- Task 66 prevents new browser storage of article/title snippets through `truthscan.history`.

### Deployment-dependent gaps

- `logger.exception` and route-level error logging can include exception text; the production sink, access permissions, retention period, and redaction policy are not defined here.
- Uvicorn/Gunicorn/hosting access logs and proxy logs were not inspected and could have different request metadata behavior.
- No repository policy establishes deletion of old browser data, aggregate stats, server logs, crash reports, or backups.
- No privacy notice, consent flow, retention schedule, or abuse-response procedure was verified.

No real token, secret, personal information, dataset row, or article content was copied into this report.

## Tests and commands actually run

Command:

```powershell
.\\.venv\\Scripts\\python.exe -m pytest tests/test_security_headers_and_endpoints.py tests/test_frontend_privacy.py tests/test_frontend_response_contract.py tests/test_application_e2e.py tests/test_readiness_contract.py tests/smoke/test_local_readiness_smoke.py -q
```

Observed result: **26 passed, 2 warnings in 4.48 seconds**.

The tests use synthetic inputs and patched unavailable-model startup paths. They do not load artifacts, inspect datasets, run inference, or access the network. No browser-level test was run.

`git diff --check` was run after creating this report and completed without errors; Git emitted the repository’s existing LF/CRLF conversion warnings for pre-existing modified files.

## Prioritized remediation plan

1. **Deployment owner decision:** choose public/restricted policy for `/docs`, `/redoc`, `/openapi.json`, `/models/info`, and `/health`; keep `/metrics` disabled unless a protected operator path is approved.
2. **CSP compatibility task:** refactor inline styles or approve a nonce/hash strategy, decide on external versus self-hosted fonts, and run report-only browser testing. Dependency: browser/staging availability and owner policy. Risk: visual breakage if enforced prematurely.
3. **Proxy/TLS task:** verify TLS termination, HSTS, forwarded headers, client-IP handling, request size/time limits, and worker topology at the eventual host. Dependency: hosting access. Risk: incorrect proxy trust can weaken rate limiting or leak transport assumptions.
4. **Logging/privacy task:** document access/application log fields, retention, redaction, operator access, deletion, and incident response. Dependency: deployment owner and privacy review. Risk: submitted text or authorization metadata may be retained outside application code.
5. **Release gates:** resolve dataset rights/provenance, trusted artifact provenance, reproducible dependencies, authorized evaluation, and final approval before enabling public inference.

## Git state and safety confirmation

- HEAD after review: `8c41ae005f4bee178a2b0104cb29049f00182081`, unchanged from the baseline.
- Final working-tree status was rechecked. The only Task 69 addition is this report under the existing untracked evaluation-results tree; no prior changes were overwritten.
- No application code, configuration, dependencies, tests, or existing reports were changed.
- No model/data/package acquisition, artifact loading, training, calibration, evaluation, inference, external service access, deployment, commit, push, tag, or destructive Git operation occurred.
- Public release remains `NO-GO`.

## Effort estimates

Next task: approximately **4–8 agent-hours** for CSP report-only compatibility work and browser validation, excluding staging/hosting access and security review. Overall remaining engineering effort before a defensible public release is approximately **35–75+ agent-hours after** rights, artifact, dependency, evaluation, scope, and authorization gates are cleared. External waiting time remains unknown.
