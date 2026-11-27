# Task 48 — Test Results

Environment: `C:\Users\gupta\AppData\Local\Programs\Python\Python312\python.exe`, Python 3.12.10.

## Regression suite

Command:

```text
python -m unittest discover -s evaluation_results/new_release_candidate-2026-10-22/task44_synthetic_prototype -p "test_*.py" -v
```

Result: exit code 0; 12 passed, 0 failed, 0 skipped. The same command was rerun as the Task 46 regression check with the same result.

## UI-specific checks

The local synthetic smoke harness exercised all three outcomes, malformed-response error handling, error-to-valid recovery, hostile-string escaping, and claim length/blank validation. Result: `UI CASES OK: outcomes, malformed error, recovery, hostile escaping`.

A static HTML check confirmed the synthetic-only disclaimer, insufficient-evidence display, Track A separation, disabled button, and absence of script/network markers.

## Not run

No browser automation was run: the artifact is static and intentionally disabled, so there is no interactive response flow to drive. No FastAPI route, network service, real evidence retrieval, model, dataset, training, evaluation, deployment, or artifact path was exercised.
