# TruthScan Trusted Provenance Audit

Date: 2026-10-21 (Asia/Calcutta)

## Executive verdict: FAIL

The real calibrated model bundle is not release-ready for production loading. The repository identifies a plausible release source and tag, but no independently trusted manifest, signing key, signed Git tag, signed release manifest, or authenticated digest was found. The current verifier correctly fails when its manifest is missing, but the downloader obtains that manifest from the same unauthenticated release source as the model files. Therefore, an attacker able to replace both the artifacts and the unsigned manifest could recompute matching hashes and pass the current integrity check.

The blocker is retained. No production artifact was downloaded, deserialized, replaced, retrained, or modified during this audit.

## Artifact origin and provenance evidence

### Repository and release contract

- Repository URL recorded by Git remote: `https://ashutosh8950@github.com/ashutosh8950/fake-news-detector.git`.
- Public release URL hard-coded in `download_models.py:24`: `https://github.com/ashutosh8950/fake-news-detector/releases/download/v2.0-calibrated-models`.
- Expected release tag: `v2.0-calibrated-models`.
- Expected downloaded files from `download_models.py:25-27` and `artifact_contract.py:14-22`:
  - `artifact_manifest.json`
  - `vectorizer.pkl`
  - `lr_calibrated.pkl`
  - `dt_calibrated.pkl`
  - `gbc_calibrated.pkl`
  - `nb_calibrated.pkl`
  - `svc_calibrated.pkl`
  - `phase2_calibration_report.json`
- The README documents the same downloader and says the five calibrated classifiers and vectorizer are placed in `models/calibrated/` (`README.md:113-130`).
- The CI workflow runs the downloader before tests (`.github/workflows/ci.yml:29-31`), so CI currently depends on this untrusted manifest path.

### Tag and source-control evidence

- Git HEAD at audit start: `8c41ae005f4bee178a2b0104cb29049f00182081` on `main`.
- Local tag `v2.0-calibrated-models` resolves directly to commit `d7df986f59860959e64a2a201f0e2e0077649240`.
- `git tag -v v2.0-calibrated-models` reported: `cannot verify a non-tag object of type commit`. This is not a signed annotated tag.
- The tag tree contains source files and no model bundle or signed manifest. The tag commit is dated 2026-09-09 and is not HEAD; later commits changed the production ensemble and downloader behavior.
- Commit authorship and the GitHub owner name are consistent with the apparent project owner, but that is repository attribution, not an independently verified cryptographic trust root.

### Local recorded provenance

- `evaluation_results/group_aware_model_evaluation/{v1,v2,v3}/source_provenance.json` and `artifact_hashes.json` record dataset/evaluation hashes and experiment outputs. These are useful reproducibility records but are not signatures over the production model bundle.
- No `models/calibrated/artifact_manifest.json` exists locally.
- The local calibrated directory contains the five required model files and vectorizer plus an extra `rfc_calibrated.pkl`; it does not establish which published release produced those bytes.
- No project-local signed manifest, detached signature, checksum signed by a separately verified key, or release attestation was found.
- A GitHub API request and release-page HEAD request were attempted for public metadata only; this environment blocked outbound GitHub sockets. No model asset request was made. The code and local Git evidence above are therefore the authoritative evidence captured in this audit.

## Trust-mechanism comparison

| Mechanism | Required evidence and trust root | Verification before deserialization | What it cannot prove | Current availability |
|---|---|---|---|---|
| Signed manifest | Manifest lists every required file, size, and digest; detached or embedded signature; signing key fingerprint verified through an independent owner-controlled channel or established key infrastructure | Verify signature and key policy, then hash every required file and reject missing/extra/unexpected entries | Correctness, training quality, absence of poisoned data, or semantic suitability | Not found |
| Signed Git tag/release process | Verifiable annotated/signed tag, trusted maintainer key, manifest committed or cryptographically bound to the tagged revision, and release asset mapping | Verify tag/signature and revision, obtain the manifest from that trusted revision, then hash staged assets | That a trusted maintainer’s build was free of compromised build inputs unless the build is reproducible/attested | Not available; local tag is unsigned and does not contain the bundle |
| Independently authenticated release digest | Digest or attestation published by a separately trusted channel, with documented authority, scope, timestamp/version, and key/identity verification | Verify the independent digest/attestation, then hash staged files before any `joblib.load` | Training provenance and compatibility beyond what the attestation covers; HTTPS alone is not enough | Not found |
| Reproduction from trusted inputs | Trusted dataset identity, source revision, dependency lockfile, deterministic/controlled build, retained logs, and independently reviewed output digest | Rebuild in isolation, validate contracts/evaluation, sign the resulting manifest, then verify it at deployment | Equivalence to the currently present bundle unless the rebuilt digest matches it | Viable remediation path; not performed in this task |

## Verifier trust-boundary review

### Confirmed safeguards

- `artifact_contract.py:42-63` fails closed on a missing, unreadable, malformed, incomplete, or unexpected manifest and validates digest/size syntax.
- `artifact_contract.py:66-82` requires exactly the defined artifact set and verifies size and SHA-256 before returning.
- `predictor.py:72-83` calls verification before any `joblib.load`, and `tests/test_artifact_contract.py:87-102` proves the synthetic tamper case does not invoke the deserializer.
- `artifact_contract.py:85-107` checks the required model set, vectorizer transformability, feature count, and model/vectorizer feature compatibility after deserialization.
- `artifact_contract.py:110-139` checks class labels `{0,1}`, `predict_proba`, output shape, finite values, and probability bounds.
- Missing or malformed trust information fails closed in synthetic tests. The readiness tests also show unavailable/invalid models do not become ready.
- `download_models.py:120-147` stages downloads, validates the staged bundle, and only then attempts activation. Exceptions return failure and remove staging content.

### Source-level gaps

1. **Manifest authenticity is absent.** `artifact_contract.py:_load_manifest` validates JSON shape and self-declared hashes, but no signature, key identity, trusted digest, or provenance binding is checked. `download_models.py:126-129` downloads the manifest from the same `GITHUB_RELEASE_URL` as the artifacts. This is the release blocker.
2. **Same-source replacement remains possible.** Replacing all downloaded files and `artifact_manifest.json` lets an attacker recompute hashes and satisfy `verify_artifact_bundle`; the verifier proves consistency, not origin.
3. **Release/tag binding is absent.** `download_models.py` does not verify a signed tag, commit, release attestation, or asset digest supplied through an independent trust channel.
4. **Activation is not cross-directory atomic.** `_activate_staged_bundle` is explicitly documented at `download_models.py:71-72` as non-atomic across `models_dir` and `metadata_dir`. Its rollback handles ordinary exceptions, but a process crash can leave a partially moved set. The verifier should still reject an incomplete/mixed set on the next load, but deployment should use a single-directory versioned bundle plus atomic pointer/symlink swap, or an equivalent transactional activation mechanism.
5. **Report schema validation is shallow.** `download_models.py:130-132` checks only that model keys exist. `predictor.py:88-105` assumes nested `held_out`, `calibration_selection`, and numeric fields; malformed trusted metadata can produce a generic exception rather than a normalized artifact-contract failure. This is not the provenance bypass, but it should be hardened before production approval.

## Smallest viable remediation path

1. The project owner should publish a versioned manifest covering exactly the eight expected files, including sizes, SHA-256 digests, model contract metadata, calibration report identity, source revision, build environment, and release tag.
2. Sign the manifest with an owner-controlled key and publish the public key/fingerprint through an independent channel. Record key rotation and revocation policy.
3. Bind the signed manifest to a signed annotated Git tag or a release attestation that names the exact manifest digest and asset digests. Do not treat GitHub HTTPS, a release page, or an unsigned adjacent checksum file as the trust root.
4. Update the downloader to verify that signature/binding before accepting the staged files; keep the current byte verification and pre-deserialization contract checks.
5. Re-stage and test the real bundle only after the signed provenance is available. If the owner cannot authenticate the existing bytes, reproduce the bundle from trusted data/source/dependencies in a controlled build and sign the resulting manifest; do not retrofit trust onto local hashes.

## Release acceptance gate

Production loading remains blocked until every item below is evidenced:

- **Trust root:** independently verified signing key or attestation identity, owner authorization, fingerprint, and rotation/revocation record.
- **Manifest:** signed manifest bound to the exact release/tag and containing all required files, no unexpected files, sizes, SHA-256 digests, source revision, build metadata, and artifact schema version.
- **Bundle completeness:** staged bundle contains the exact required five calibrated models, vectorizer, and calibration report; no missing or silently substituted files.
- **Model contract:** trusted real-artifact test confirms labels `{0,1}`, the intended Real-class probability column, finite `(1,2)` probabilities, and prediction interface behavior.
- **Feature compatibility:** real vectorizer/model feature dimensions match; preprocessing configuration and feature vocabulary contract are compatible.
- **Calibration compatibility:** report schema, model keys, selected calibration method, held-out metrics, and ensemble metadata are structurally and semantically compatible with `predictor.py`.
- **Safe activation:** download into an isolated versioned staging directory, verify signature and all hashes, run contract tests, then activate atomically; failed activation leaves the prior known-good bundle available.
- **Tests:** synthetic fail-closed tests, tamper-before-deserialization test, missing/malformed trust tests, real-bundle contract tests, startup readiness tests, and deployment smoke tests all pass.
- **Deployment validation:** clean environment, pinned dependencies, no network requirement at inference, health/readiness behavior, rollback drill, and resource limits are validated.
- **Audit evidence:** retain signed manifest, public-key fingerprint, release/tag identity, asset URLs, digests/sizes, build logs, dependency lockfile, test results, deployment approval, and rollback record.

The following must be reported separately and must not be conflated:

- Source-code safeguards demonstrated by synthetic tests: **demonstrated**.
- Provenance of the real local model bundle: **not established**.
- Compatibility of trusted real artifacts: **not established**.
- Production deployment approval: **not granted**.

## Exact files inspected and commands executed

Files inspected:

- `download_models.py`
- `artifact_contract.py`
- `predictor.py`
- `README.md`
- `config.py`
- `Dockerfile`
- `render.yaml`
- `.github/workflows/ci.yml`
- `tests/test_artifact_contract.py`
- `tests/test_readiness_contract.py`
- `evaluation_results/group_aware_model_evaluation/v1/source_provenance.json`
- `evaluation_results/group_aware_model_evaluation/v1/artifact_hashes.json`
- corresponding `v2` and `v3` provenance/hash/validation records
- repository metadata and file names under `models/` (binary contents not read)

Commands/actions executed:

- `Get-Location; git rev-parse HEAD; git status --short; Get-ChildItem ...`
- repository-wide `rg` search for release, manifest, digest, signature, provenance, and model references
- numbered source inspection of the files above
- `git remote -v`
- `git tag --list --format=...`
- `git tag -v v2.0-calibrated-models`
- `git cat-file -p v2.0-calibrated-models`
- `git ls-tree -r --name-only v2.0-calibrated-models`
- `git log --decorate --oneline ...` and release-URL history searches
- metadata-only existence/name checks under `models/calibrated/`
- `\.venv\Scripts\python.exe -m pytest tests/test_artifact_contract.py tests/test_readiness_contract.py -q`
- public GitHub metadata/API and release-page HEAD attempts; outbound sockets were blocked, and no model asset request was made

Test result: **18 passed**, with two existing deprecation warnings. These tests use synthetic bundles and mocks; they do not validate the real production files.

## Git state and task status

### Before audit

- HEAD: `8c41ae005f4bee178a2b0104cb29049f00182081`
- Branch: `main`
- Existing modifications/untracked files were preserved, including changes to `README.md`, `app.py`, `download_models.py`, `frontend/style.css`, `predictor.py`, `routers/api.py`, documentation files, existing evaluation directories, `artifact_contract.py`, `duplicate_aware_manifest.py`, and tests.

### After audit

- HEAD remains `8c41ae005f4bee178a2b0104cb29049f00182081`.
- No production source or artifact file was edited.
- One new audit directory/report was added: `evaluation_results/trusted_provenance_audit_2026-10-21/TRUSTED_PROVENANCE_AUDIT.md`.
- Existing working-tree changes remain preserved; the new report is the only audit-created deliverable.

## Final status and estimate

- Work completed: provenance trace, tag/release evidence review, trust-option comparison, verifier trust-boundary review, synthetic safeguard test run, and audit report.
- Work remaining: obtain independently authenticated release provenance or reproduce and sign the artifacts; then implement/verify the provenance check and run trusted real-artifact compatibility and deployment gates.
- Approximate next-task duration after signed provenance is supplied: 2-4 hours for verifier integration and trusted real-artifact validation, excluding any model rebuild.
- Approximate total remaining duration if reproduction is required: 1-2 business days, depending on controlled build time and owner review.

