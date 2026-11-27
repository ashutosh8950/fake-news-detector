# Task 66 — Browser History Privacy Fix

**Date:** 2026-10-27  
**Release posture:** `NO-GO` for public Fake/Real inference

## Summary

Removed default browser persistence of submitted article/title content. The frontend now retires the legacy `truthscan.history` key narrowly, keeps analysis history in memory for the current page session, and displays generic session-only history text instead of article excerpts.

Unrelated browser storage, including `truthscan.stats` and `truthscan.theme`, remains intact. No model, API, Track B, deployment, or release behavior was changed.

## Files inspected

- `evaluation_results/new_release_candidate_2026-10-22/task65_model_free_security_privacy_review/TASK65_MODEL_FREE_SECURITY_PRIVACY_REVIEW.md`
- `frontend/app.js`
- `frontend/index.html`
- `tests/test_frontend_response_contract.py`
- `tests/test_application_e2e.py`
- `tests/smoke/test_local_readiness_smoke.py`

## Files changed or created

- `frontend/app.js` — removed content-bearing browser history persistence and legacy history restoration.
- `tests/test_frontend_privacy.py` — added synthetic privacy regression tests.
- `evaluation_results/new_release_candidate_2026-10-22/task66_browser_history_privacy_fix/TASK66_BROWSER_HISTORY_PRIVACY_FIX.md` — this report.

The frontend file already contained unrelated pre-existing working-tree changes. Those were preserved; this task changed only the history-retention and related submission call sites.

## Privacy behavior before and after

### Before

After a successful analysis, `recordAnalysis(result, title || text)` stored:

```text
snippet: snippetSource.slice(0, 120)
```

The resulting `truthscan.history` JSON was written to `localStorage` and restored on later page loads. The UI rendered the stored snippet.

### After

- `localStorage.removeItem(STORAGE.history)` retires only the legacy history key at startup.
- `state.history` starts as an empty in-memory array rather than loading from storage.
- `recordAnalysis(result)` stores only non-content metadata in the current page session.
- No article title, body, or `snippetSource` is written to browser storage.
- History rendering displays `Article analyzed in this session` rather than submitted content.
- The Clear history action removes only `truthscan.history` and continues to reset aggregate stats.
- `truthscan.stats` and `truthscan.theme` remain separate and are not cleared by the privacy migration.

This change does not claim that previously stored data has been removed from browser backups, browser profiles, synced storage, screenshots, server logs, or other devices. It only removes the key when the updated application runs and prevents new content persistence through this path.

## Regression tests added

`tests/test_frontend_privacy.py` checks the real frontend source for the privacy contract:

1. History is not loaded from storage, `snippetSource` is absent, and the submission path calls `recordAnalysis(result)` without article content.
2. The legacy history key is removed narrowly while unrelated theme/stat storage remains present; `localStorage.clear()` is not used.
3. History rendering uses generic session text and does not read or render `h.snippet`.

These are source-level frontend checks because no browser automation framework was available in the documented environment. They do not claim a real browser interaction occurred.

## Tests executed

Command:

```powershell
.\.venv\Scripts\python.exe -m pytest tests/test_frontend_privacy.py tests/test_frontend_response_contract.py tests/test_readiness_contract.py tests/smoke/test_local_readiness_smoke.py tests/test_api.py -q
```

Result:

```text
27 passed, 2 warnings in 10.58s
```

The warnings were existing FastAPI/Starlette/httpx and AnyIO deprecation warnings. The suite exercised frontend contract/privacy assertions and model-free unavailable-model behavior; no model artifacts or datasets were loaded or accessed.

Additional validation:

- `git diff --check` completed without errors; existing LF/CRLF conversion warnings remained.
- The final report directory contains only this report.
- No browser-level test was run.
- No application server was started.

## Limitations and follow-up privacy concerns

- Current-session history still exists in JavaScript memory until the page is refreshed or cleared. It is not persisted by this change.
- Aggregate statistics remain in `truthscan.stats`; they do not contain article text but may still be undesirable for a privacy-sensitive deployment.
- Server-side log retention, reverse-proxy access logs, TLS, monitoring, and deployment storage were not established by this local change.
- A public service still needs an owner-approved privacy notice, retention/deletion policy, abuse controls, and security/deployment review.
- Existing data in old browser profiles or backups is outside the application’s control and was not inspected.

## Git state

- HEAD before and after: `8c41ae005f4bee178a2b0104cb29049f00182081`.
- Initial working-tree status count: 47 entries.
- Final working-tree status count: 48 entries, reflecting the new privacy test/report additions; all prior entries were preserved.
- No unrelated tracked files were reverted or overwritten.

## Restricted activities

No dataset acquisition or article-data inspection occurred. No model or serialized artifact was loaded. No training, calibration, evaluation, inference, package installation, external contact, deployment, publication, commit, push, tag, or destructive Git operation occurred. Track A behavior, Track B isolation, release gates, and the public `NO-GO` status remain unchanged.

## Next-task estimate

The next bounded task should review deployment-level privacy behavior—server/access-log retention, security headers, `/metrics` exposure, proxy/client-IP handling, and abuse controls—without enabling inference. Estimated engineering effort is approximately 4–8 agent-hours, excluding owner/security review.

Approximate remaining engineering effort before a defensible public release is 35–75+ agent-hours after dataset rights, artifact trust, dependency reproducibility, evaluation authorization, and scope decisions are resolved. External waiting time remains unknown and is excluded.
