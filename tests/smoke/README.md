# TruthScan model-free readiness smoke test

Run this one command from the repository root in Windows PowerShell:

```text
.\scripts\run_safe_local_verification.ps1
```

The runner uses `.venv\Scripts\python.exe`, runs the four model-free readiness smoke tests first, then runs the 20 isolated synthetic Track B API/demo regression tests. It stops with a non-zero exit code if either group fails.

The harness uses the real FastAPI application, routes, and served homepage through `TestClient`. It patches the startup model-loading, preprocessing warmup, and DistilBERT-loading calls so no trusted model artifact or external resource is loaded.

Expected checks:

- `/` returns HTTP 200 and serves the TruthScan page.
- `/health` returns HTTP 503 with `status: "not_ready"` and `models_loaded: false`.
- A valid-looking `/analyze` request returns HTTP 503 without Fake/Real prediction fields.
- Malformed analysis input returns HTTP 422 and never reaches prediction.

Pytest and the runner return a non-zero process exit code when any assertion fails. This verification is not browser testing, real inference, model validation, or release approval. It does not run the full application suite, model-dependent tests, training, calibration, or dataset processing.
