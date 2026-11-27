# TruthScan Candidate Environment Dependency Inventory

This inventory separates the synthetic CI environment from future model and candidate-build environments. It is based on local static inspection and the existing `.venv`; it is not a signed release record or a complete offline lock.

## Synthetic/core CI

The CI lock is [requirements-ci.lock](requirements-ci.lock). It pins the exact versions observed in the existing Python 3.11.9 environment, excluding the spaCy language-model package and a Windows-only package that are not needed by the CI test selection.

The CI suite imports FastAPI, Pydantic, HTTPX/TestClient, pytest, NumPy, scikit-learn, joblib, spaCy, Loguru, SlowAPI, and the repository's pure-Python contract modules. The lock retains the relevant transitive packages captured by `pip freeze --all`.

## Future inference/runtime environment

Additional runtime requirements include:

- `en_core_web_sm` 3.8.0, installed separately from spaCy. Its observed wheel URL and SHA-256 were recorded by the local environment, but the package is deliberately excluded from CI.
- Verified model artifacts and their authenticated manifest, which are not available as trusted release inputs.
- Optional DistilBERT dependencies and model resources, which are not installed in the verified environment and are not required for the standard ensemble path.

The runtime environment therefore cannot yet be accepted as a complete reproducible production environment.

## Future training/calibration environment

Training and calibration additionally require pandas, NumPy, scikit-learn, joblib, spaCy, the language model, repository training/calibration scripts, exact dataset inputs, grouping/partition policy, seeds, and calibration configuration. The local repository does not provide an authenticated complete lock and does not establish dataset rights or historical bundle equivalence.

## Integrity and reproducibility limits

- Exact versions are pinned in the CI specification.
- `pip check` passed in the existing environment.
- No local wheel or source-distribution cache was available, so package artifact hashes were not added.
- The lock is not an offline-install bundle and does not authenticate package publishers.
- The existing dependency declarations remain broader and looser than this candidate-only CI lock.
- A future stronger lock should be generated from a controlled package mirror or reviewed artifact set, with hashes and an authenticated environment record retained with the release evidence.
