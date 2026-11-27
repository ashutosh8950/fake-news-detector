# Task 25 — Environment Reproducibility Report

**Date:** 2026-10-22  
**Executive result:** **CONDITIONAL PASS**  
**Scope:** Read-only environment/dependency audit. No real dataset processing, model loading, training, installation, download, or production change occurred.

## Executive conclusion

The existing repository `.venv` is the suitable environment for future candidate-only work because it uses Python 3.11.9 and contains the application, training, calibration, test, serialization, spaCy, and language-model dependencies observed locally. The default Python environment is not interchangeable: it is Python 3.12.10, lacks spaCy and the application runtime stack, and has different NumPy, pandas, SciPy, scikit-learn, pytest, and httpx versions.

An exact installed-version snapshot was created at [venv_freeze_all.txt](venv_freeze_all.txt). A complete defensible dependency lock was **not** produced. The snapshot does not establish package-artifact hashes, an authenticated package source, a verified offline wheelhouse, or reproducible installation without network access. The spaCy language model is recorded separately with its installed version and metadata-only direct-URL hash.

The candidate release remains blocked independently by dataset provenance/licensing, approved grouping and partition evidence, isolated runner review, and release authentication.

## Environment captured

### Candidate `.venv`

Observed facts:

- Path: `C:\Users\gupta\Downloads\FAKE_NEWS_DETECTION\.venv`
- Python: 3.11.9, 64-bit Windows
- Executable: `C:\Users\gupta\Downloads\FAKE_NEWS_DETECTION\.venv\Scripts\python.exe`
- pip: 24.0
- `pip freeze --all`: 77 entries
- `pip check`: `No broken requirements found.`
- spaCy: 3.8.16
- `en_core_web_sm`: installed package version 3.8.0; discoverable via `spacy.util.is_package`; installed under the `.venv` site-packages directory
- Candidate-relevant versions: FastAPI 0.141.1, Uvicorn 0.53.0, Gunicorn 26.2.0, scikit-learn 1.9.0, pandas 3.0.6, NumPy 2.4.6, SciPy 1.17.1, joblib 1.6.0, requests 2.34.2, loguru 0.7.3, pydantic-settings 2.15.0, slowapi 0.1.10, pytest 9.1.1, httpx 0.28.1, python-multipart 0.0.32, and aiofiles 25.1.0.

The machine-readable record is [environment_inventory.json](environment_inventory.json).

### Default Python

Observed facts:

- Path: `C:\Users\gupta\AppData\Local\Programs\Python\Python312\python.exe`
- Python: 3.12.10, 64-bit Windows
- pip: 25.0.1
- `pip freeze --all`: 151 entries
- `pip check`: `No broken requirements found.`
- scikit-learn 1.3.2, pandas 2.1.4, NumPy 1.26.4, SciPy 1.17.1, joblib 1.6.0, requests 2.32.3, pytest 8.3.5, and httpx 0.27.0 were present.
- spaCy, `en_core_web_sm`, FastAPI, Uvicorn, Gunicorn, pydantic-settings, slowapi, python-multipart, and aiofiles were not installed according to package metadata.

Inference: the default environment is unsuitable for candidate work because it cannot execute the declared preprocessing/runtime path without additional installation and its scientific-library versions differ from the `.venv`. This conclusion is based on observed package metadata, not on a model execution.

## spaCy model record

The installed distribution metadata reports:

- Name: `en_core_web_sm`
- Version: 3.8.0
- Direct URL: `https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.8.0/en_core_web_sm-3.8.0-py3-none-any.whl`
- Metadata-declared SHA-256: `1932429db727d4bff3deed6b34cfc05df17794f4a52eeb26cf8928f7c1a0fb85`
- Compatibility metadata: spaCy `>=3.8.0,<3.9.0`
- Installed location: `.venv\Lib\site-packages`

The version and direct URL were observed through installed distribution metadata. The hash was **not** recomputed from a retained wheel or independently authenticated artifact and is therefore recorded as `metadata_only_not_artifact_verified` in `environment_inventory.json`.

The model was not downloaded or loaded in this task. `spacy.util.is_package()` was used only to confirm package discoverability.

## Declaration and import audit

### `requirements.txt`

The declaration contains only one exact application pin: `scikit-learn==1.9.0`. FastAPI, Uvicorn, pandas, NumPy, spaCy, python-multipart, aiofiles, requests, joblib, Gunicorn, pytest, httpx, loguru, pydantic-settings, and slowapi are unpinned or lower-bounded. It is not a complete lock.

The `.venv` happens to satisfy the scikit-learn pin and has newer exact versions for many other packages, but that is an observation about this environment, not a reproducibility guarantee.

### Deployment and CI declarations

- `Dockerfile` uses mutable `python:3.11-slim`, installs `requirements.txt`, runs `pip install --upgrade pip`, and executes `python -m spacy download en_core_web_sm` without pinning the model asset or retaining its artifact hash. It then runs `download_models.py`.
- `render.yaml` runs the same unpinned requirements/model download flow and declares `PYTHON_VERSION: 3.11.0`, which differs from the local `.venv` patch version 3.11.9.
- `.github/workflows/ci.yml` sets up Python 3.11, installs the mutable requirements, downloads the spaCy model, downloads calibrated models, and runs tests. It does not provide a lock, package hashes, wheelhouse, or authenticated model-resource record.

### Relevant imports and external resources

- Preprocessing imports spaCy and loads `en_core_web_sm` at module import (`preprocessor.py:13-16`).
- Training/calibration/evaluation use pandas, NumPy, scikit-learn, joblib, loguru, and the preprocessing module.
- API/runtime code uses FastAPI, Starlette/Uvicorn, Gunicorn, pydantic, pydantic-settings, loguru, slowapi, requests-related downloader code, and joblib/NumPy through prediction.
- The optional DistilBERT path attempts to import `transformers` and can load `GuptaAshutosh/truthscan-fake-news-distilbert` from Hugging Face at runtime (`distilbert_predictor.py:4-31`). `transformers`, its transitive dependencies, and that model resource are not declared in `requirements.txt` and were not installed/downloaded here.
- `download_data.py` can fetch datasets from Hugging Face/Kaggle, and `download_models.py` fetches release artifacts. These are mutable external resources and are outside this candidate environment snapshot.

Observed fact: the standard five-model path and optional DistilBERT path do not have the same dependency/resource boundary. Inference: any future release record must state explicitly whether the optional path is in scope rather than assuming the base requirements describe every application capability.

## Local cache and lock feasibility

The pip cache was inspected read-only:

- HTTP cache size was approximately 2.7 GB with 3,300 HTTP cache files.
- No locally built wheels were cached.
- The cache was not treated as a package-artifact repository because its entries were not mapped to a reviewed package set or independently authenticated hashes.

The installed `.venv` freeze is useful for reconstructing the observed environment at the version level, but it is not sufficient to produce a secure lock with artifact hashes. No package wheel hashes were verified from actual retained artifacts. No complete offline installation source was identified.

## Consistency checks

Commands and results:

```text
git rev-parse HEAD
=> 8c41ae005f4bee178a2b0104cb29049f00182081

python --version
=> Python 3.12.10
python -m pip --version
=> pip 25.0.1 ... Python312 ...
python -m pip freeze --all
=> 151 entries
python -m pip check
=> No broken requirements found.

.venv\Scripts\python.exe --version
=> Python 3.11.9
.venv\Scripts\python.exe -m pip --version
=> pip 24.0 ... Python311 ...
.venv\Scripts\python.exe -m pip freeze --all
=> 77 entries, retained in venv_freeze_all.txt
.venv\Scripts\python.exe -m pip check
=> No broken requirements found.

.venv\Scripts\python.exe -c "inspect package metadata, spaCy version,
spacy.util.is_package('en_core_web_sm'), model direct_url.json"
=> spaCy 3.8.16; en_core_web_sm 3.8.0; installed and discoverable;
   direct URL and metadata-declared SHA-256 observed.

.venv\Scripts\python.exe -m pip cache info
=> HTTP cache present; no locally built wheels cached.

.venv\Scripts\python.exe -m pip cache list
=> No locally built wheels cached.
```

An attempted informational command using `pip cache list --format=columns` was rejected by pip 24.0 because that format is unsupported. The supported `pip cache list` command was then run successfully; no cache mutation occurred.

No dependency installation, package upgrade, model download, dataset download, model loading, or training command was run.

## Lock decision

**Complete secure lock:** not feasible from available local evidence.

**Created instead:**

- exact installed-version snapshot: [venv_freeze_all.txt](venv_freeze_all.txt);
- machine-readable inventory: [environment_inventory.json](environment_inventory.json); and
- lock-gap and future lock-generation plan: [TASK25_LOCK_GAP.md](TASK25_LOCK_GAP.md).

The snapshot pins observed distribution versions, but it does not pin or authenticate the package artifacts themselves. The spaCy model is represented as a direct URL in the freeze and inventory, but its hash remains metadata-only. Offline reconstruction is therefore **not established**.

## Required next environment task

After the project owner approves the candidate’s dependency scope, create a clean environment using a reviewed lock-generation process, retain the exact package wheels and spaCy model wheel in a controlled wheelhouse, compute hashes from those artifacts, test installation with network access disabled, and authenticate the resulting lock/wheelhouse record. Keep optional DistilBERT dependencies and its external model resource either separately locked and authenticated or explicitly out of the release scope.

This task did not generate that lock or alter any production declaration.

## Git and safety audit

Before the task:

- HEAD: `8c41ae005f4bee178a2b0104cb29049f00182081`.
- Existing modified files: `README.md`, `app.py`, `download_models.py`, `frontend/style.css`, `predictor.py`, `routers/api.py`.
- Existing untracked files/directories included prior reports, tests, documentation, and the candidate harness.

After the task:

- HEAD remains `8c41ae005f4bee178a2b0104cb29049f00182081`.
- Existing changes and untracked files remain preserved.
- New files are confined to `evaluation_results/new_release_candidate_2026-10-22/environment_task25/`.
- No `requirements.txt`, Dockerfile, Render configuration, production code, harness file, prior report, model artifact, Git metadata, or existing evaluation result was modified.

No real training dataset was processed for training or evaluation. No production model artifact was loaded, downloaded, modified, or replaced. No package or language model was installed or downloaded. No commit, push, deployment, signing, or release occurred.

**Final status:** environment characterized; exact installed snapshot available; complete authenticated dependency lock and offline reconstruction remain unresolved.
