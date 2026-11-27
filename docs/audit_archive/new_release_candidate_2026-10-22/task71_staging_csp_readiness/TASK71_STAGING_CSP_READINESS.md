# Task 71 — Staging CSP Report-Only Test Readiness Gate

**Assessment date:** 2026-10-27  
**Readiness decision:** **BLOCKED — APPROVAL OR INFRASTRUCTURE MISSING**  
**Public release posture:** `NO-GO`

This assessment prepares a controlled browser test but does not activate CSP, contact a hosting provider, access staging, or change application files.

## Baseline and evidence status

HEAD before assessment: `8c41ae005f4bee178a2b0104cb29049f00182081`. The working tree already contained extensive tracked modifications and untracked project/report files. They were preserved.

Task 69 and Task 70 were read as prior evidence. Their claims were independently checked against the current source inventory below where possible; prior browser/staging claims were not treated as reproduced. No approved staging URL, credentials, deployment-owner approval, CSP collector, or rollback record was found in the repository.

## Files and code locations inspected

- `evaluation_results/new_release_candidate_2026-10-22/task69_csp_docs_exposure_review/TASK69_CSP_DOCS_EXPOSURE_REVIEW.md`
- `evaluation_results/new_release_candidate_2026-10-22/task70_csp_deployment_decision_register/TASK70_CSP_DEPLOYMENT_DECISION_REGISTER.md`
- `app.py:78-103` — FastAPI construction and current security-header middleware
- `routers/api.py:20, 57-109` — readiness, metrics gate, and operational routes
- `frontend/index.html:8-11, 73-103, 188-192, 237, 296-297`
- `frontend/app.js:216-267, 297-426, 473-520`
- `frontend/style.css`, `frontend/response_contract.js`
- `render.yaml`, `Dockerfile`, `.github/workflows/ci.yml`
- `tests/test_security_headers_and_endpoints.py`, `tests/test_application_e2e.py`, `tests/test_frontend_privacy.py`, `tests/test_frontend_response_contract.py`, `tests/test_readiness_contract.py`, `tests/smoke/test_local_readiness_smoke.py`

## Independently reproduced current behavior

- No CSP or CSP Report-Only directive exists in the inspected repository files.
- The existing application security headers are present in `app.py`.
- `/docs`, `/redoc`, and `/openapi.json` remain enabled by FastAPI defaults.
- `/metrics` has Task 68’s default-deny/token-gated behavior.
- The frontend uses same-origin scripts and CSS, Google Fonts, inline style attributes, inline SVG style attributes, and dynamic HTML with inline animation styles.
- The application source contains no CSP report endpoint or report collector.

These observations do not establish behavior at a hosting proxy or in a browser.

## Authorized browser test matrix

The following matrix is ready to use only after staging approval, an approved URL, and a controlled test scope are supplied. All test inputs must be synthetic and must not contain personal, confidential, or real article content.

| ID | Test | Expected behavior | Evidence to capture safely | Pass/fail criterion |
|---|---|---|---|---|
| C-01 | Initial page load | Page renders without CSP console violations that block essential UI | Screenshot, console summary, response headers; redact URLs/query values if needed | PASS if essential UI loads and only documented/non-blocking reports occur |
| C-02 | Local scripts and CSS | `/static/response_contract.js`, `/static/app.js`, and `/static/style.css` load under Report-Only | Console/network resource names only | PASS if all load; FAIL if blocked or runtime error occurs |
| C-03 | Inline styles/SVG | Existing visual layout and animations remain usable while violations are reported | Console directive/source summary and screenshot | PASS if UI remains functional; record each violation for refactoring |
| C-04 | Google Fonts | Fonts load if explicitly allowed, or documented fallback renders acceptably | Screenshot and resource status, without user data | PASS if approved font/fallback is readable and no essential UI breaks |
| C-05 | Form validation | Empty/short synthetic input shows validation and no prediction | Screenshot, console summary | PASS if validation remains controlled and no Fake/Real result appears |
| C-06 | Unavailable-model flow | Synthetic valid-looking input shows truthful unavailable state | Screenshot, response status/body fields limited to synthetic readiness data | PASS if HTTP 503 is handled without fabricated prediction |
| C-07 | API error flow | Offline/malformed synthetic response yields controlled error and controls recover | Screenshot, console error count, synthetic stub details | PASS if no unhandled exception or stale result remains |
| C-08 | Dynamic result/history rendering | Synthetic contract-valid response renders; Task 66 generic session history remains content-free | Screenshot and DOM/console summary; no submitted content in evidence | PASS if rendering works and no article text is persisted/displayed from old storage |
| C-09 | Security headers | Existing non-CSP headers remain present through staging proxy | Sanitized response-header capture | PASS if expected headers are preserved or approved proxy behavior is documented |
| C-10 | Docs endpoints | `/docs`, `/redoc`, and `/openapi.json` match approved exposure policy | Status/header capture only | PASS only if owner-approved access policy is enforced |
| C-11 | CSP Report-Only versus enforcement | Report-Only logs violations but does not block resources; enforcement is not part of this gate | Header comparison and console summary | PASS if Report-Only semantics are observed; enforcement must be a separate approved stage |
| C-12 | Privacy regression | No article/title content enters browser storage; metrics token is never exposed | Storage-key names only, synthetic test, no values | PASS if `truthscan.history` is absent and unrelated keys remain intact |

## Proposed report-only delivery

No delivery mechanism exists in the repository. An authorized staging operator would need to add a temporary `Content-Security-Policy-Report-Only` header at the approved staging boundary, using the candidate policy from Task 70 only after reviewing its compatibility trade-offs. The current page’s inline styles mean a strict final `style-src` will require refactoring or an approved nonce/hash approach; this cannot be decided from source inspection alone.

If no collector is available, use browser-console violation summaries and sanitized screenshots as evidence. Do not add a public collector for this test. If a collector is approved, it must:

- accept only staging reports;
- redact query strings, authorization values, tokens, user identifiers, and any submitted-content fields;
- retain only the minimum directive/source/path metadata needed for compatibility work;
- restrict access to approved reviewers;
- have a documented deletion date and rollback procedure;
- never be used as a general application logging endpoint.

No CSP report endpoint or collector was found in the repository.

## Prerequisite checklist

| Prerequisite | Status | Evidence needed |
|---|---|---|
| Written deployment-owner approval for a staging Report-Only test | **BLOCKED** | Named approval, scope, and expiration/rollback authority |
| Authorized staging URL | **BLOCKED** | Exact URL and confirmation it is the intended environment |
| Authorized browser/test scope | **BLOCKED** | Approved tester, browser/version, synthetic-only input rule, and allowed routes |
| Confirmation that staging uses synthetic/no-model test behavior | **UNVERIFIED** | Environment confirmation that no untrusted model/data work is triggered |
| Approved Report-Only delivery mechanism | **BLOCKED** | Staging proxy/app header configuration and exact policy version |
| Safe violation evidence path | **BLOCKED** | Sanitized console workflow or approved restricted collector |
| CSP report retention/redaction policy | **UNVERIFIED** | Fields retained, access list, deletion date, and redaction test |
| Baseline local security-header/readiness tests | **VERIFIED LOCALLY** | This task’s command: 26 passed, 2 warnings |
| Staging response-header baseline | **BLOCKED** | Sanitized headers from the approved URL |
| Rollback procedure | **BLOCKED** | Owner-approved removal/reversion steps and confirmation path |
| Documentation/metrics endpoint exposure decision | **PENDING OWNER DECISION** | Policy for `/docs`, `/redoc`, `/openapi.json`, `/models/info`, `/health`, and `/metrics` |

Because several required items are blocked, this assessment cannot return `READY FOR AUTHORIZED STAGING TEST`.

## Rollback requirements

Before any staging change, the owner should record:

1. The exact pre-test response-header configuration.
2. The temporary CSP policy and its delivery location.
3. A time-bounded rollback owner.
4. The precise removal/reversion action for the Report-Only header and any collector route/configuration.
5. A post-rollback check confirming the baseline headers, page load, and model-unavailable behavior.

Rollback must not enable inference, remove fail-closed checks, expose `/metrics`, or broaden documentation access.

## Safe local validation actually run

Command:

```powershell
.\\.venv\\Scripts\\python.exe -m pytest tests/test_security_headers_and_endpoints.py tests/test_application_e2e.py tests/test_frontend_privacy.py tests/test_frontend_response_contract.py tests/test_readiness_contract.py tests/smoke/test_local_readiness_smoke.py -q
```

Observed result: **26 passed, 2 warnings in 9.41 seconds**. The warnings were existing FastAPI/Starlette/httpx and AnyIO deprecation warnings. These tests use synthetic inputs and patched unavailable-model startup paths; they do not test a browser, staging, CSP, or hosting proxy.

`git diff --check` was run after creating the report and completed without errors; existing LF/CRLF conversion warnings were emitted for pre-existing modified files.

## Limitations and recommended next action

No browser interaction occurred, no external URL was contacted, and no staging environment was identified or approved. Therefore CSP compatibility, report-only semantics, proxy header preservation, TLS/HSTS, endpoint exposure, and deployment log handling remain unverified.

Recommended next action: obtain the deployment owner’s written staging approval, exact URL, synthetic-only scope, approved Report-Only delivery mechanism, safe evidence/retention path, and rollback owner. Only then run the matrix above without enforcing CSP.

## Final state and restrictions

- HEAD after assessment: `8c41ae005f4bee178a2b0104cb29049f00182081`, unchanged.
- Final working-tree status was rechecked; this Task 71 report is the only new artifact from this task under the existing untracked evaluation-results tree.
- No application code, configuration, tests, dependencies, or previous reports were modified.
- No datasets, article rows, models, packages, external services, staging URLs, credentials, browser sessions, training, calibration, evaluation, inference, deployment, commit, push, or tag operations occurred.
- Public release remains `NO-GO`.
