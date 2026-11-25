# Historical Release Recovery Audit

**Project:** TruthScan / fake-news-detector  
**Audit date:** 2026-10-22  
**Scope:** Public, read-only provenance investigation. No model binaries were downloaded or loaded.

## Executive verdict

**FAIL — historical release provenance remains unauthenticated.**

Public records establish that `ashutosh8950` publicly describes the project and that related public dataset pages exist. They do not independently authenticate the local production bundle, bind its files to a source revision and dataset release, or provide a trusted reference for functional or byte-identical reproduction.

The exact project GitHub release, tag, asset, and workflow pages were queried through the public read-only source but were unavailable to the retrieval service (`Cache miss`). This is an access limitation, not evidence that those records do not exist. The local `v2.0-calibrated-models` tag is unsigned according to the prior local audit evidence, and the local downloader obtains the manifest from the same release location as the artifacts. The release blocker therefore remains active.

## Sources inspected

| Source | Date/revision | Classification | What it establishes | What it does not establish |
|---|---|---|---|---|
| [Project owner GitHub profile](https://github.com/ashutosh8950) | Public profile inspected 2026-10-22 | AUTHORITATIVE BUT NOT CRYPTOGRAPHICALLY AUTHENTICATED | Publicly associates `ashutosh8950` with the Fake News Detector project and describes its intended architecture and claims. | It does not authenticate any model file, dataset copy, release asset, or historical build. |
| [Project repository](https://github.com/ashutosh8950/fake-news-detector) | Queried 2026-10-22; exact page unavailable to the retrieval service | UNAVAILABLE | The requested repository URL and its expected release namespace were identified. | No release metadata, asset digest, signature, attestation, or workflow result could be verified from this query. |
| [Project releases](https://github.com/ashutosh8950/fake-news-detector/releases) | Queried 2026-10-22; unavailable to the retrieval service | UNAVAILABLE | Nothing beyond the intended public endpoint. | It cannot support an assertion that releases or assets are absent. |
| [Project release tag](https://github.com/ashutosh8950/fake-news-detector/releases/tag/v2.0-calibrated-models) | Queried 2026-10-22; unavailable to the retrieval service | UNAVAILABLE | Nothing beyond the requested tag URL. | No publication date, commit association, asset list, checksum, signature, or attestation was verified. |
| [GonzaloA/fake_news dataset](https://huggingface.co/datasets/GonzaloA/fake_news/tree/main) | Public page revision shown as `d653ddb`; inspected 2026-10-22 | AUTHORITATIVE BUT NOT CRYPTOGRAPHICALLY AUTHENTICATED | A public dataset repository exists with train/test/evaluation files, tabular/text metadata, history, and a named owner. | It does not prove that local `data/Fake.csv` and `data/True.csv` came from this repository or a particular commit. |
| [Dataset history commit](https://huggingface.co/datasets/GonzaloA/fake_news/commit/b690c7927f78544dc08a6a4817e50e7384182024) | Commit `b690c7927f78544dc08a6a4817e50e7384182024`; inspected 2026-10-22 | AUTHORITATIVE BUT NOT CRYPTOGRAPHICALLY AUTHENTICATED | The public dataset card records split counts and says the data were assembled from other fake-news datasets; its licensing field was `unknown` / information needed. | It does not provide an authenticated mapping to the local CSV files, a signed source release, or a publisher checksum for those exact files. |
| [Kaggle Fake and Real News Dataset](https://www.kaggle.com/datasets/clmentbisaillon/fake-and-real-news-dataset) | Public page metadata inspected 2026-10-22; version 1 | AUTHORITATIVE BUT NOT CRYPTOGRAPHICALLY AUTHENTICATED | A public dataset page lists `Fake.csv` and `True.csv`, eight columns, and approximately 116.37 MB. | The accessible metadata did not establish a signed checksum, acquisition record, or cryptographic mapping to the local files. |
| [GitHub release/tag documentation](https://docs.github.com/en/repositories/releasing-projects-on-github/viewing-your-repositorys-releases-and-tags?apiVersion=2022-11-28) | Documentation inspected 2026-10-22 | AUTHORITATIVE PROCEDURAL DOCUMENTATION | Explains where public release and tag history is normally exposed. | It is not evidence about this repository's release, signatures, or artifact contents. |

The public dataset pages are useful source leads, not independent authentication of the local data. A hosted checksum or manifest would still require an independently trusted channel for the checksum authority and the release identity.

## Release, tag, signature, and attestation findings

The local repository evidence reviewed by the preceding audits identifies the expected release URL as:

`https://github.com/ashutosh8950/fake-news-detector/releases/download/v2.0-calibrated-models`

The downloader expects `artifact_manifest.json`, `vectorizer.pkl`, five calibrated model files, and the Phase 2 report. The local downloader obtains the manifest from the same unauthenticated release source as the artifacts. No tracked local artifact-manifest generator, independently authenticated checksum record, signed manifest, CI attestation, or preserved trusted reference output was found in the prior local evidence.

The local tag `v2.0-calibrated-models` was previously inspected and resolves to an unsigned commit. That is consistency evidence about the local Git object graph, not an independently verified release signature. A public GitHub URL, HTTPS transport, release description, unsigned tag, or checksum stored beside the artifacts cannot establish historical authenticity against an attacker able to replace the source and its metadata together.

The exact GitHub release, tag, and workflow pages could not be retrieved by the public web source used for this audit. Consequently, no conclusion of absence is made about GitHub release assets, signatures, workflow runs, or attestations; they remain unverified and unavailable for this audit.

## Dataset provenance findings

Local documentation and scripts identify the public Hugging Face `GonzaloA/fake_news` dataset as the primary download source and a Kaggle dataset as a fallback. Public records confirm that both dataset pages exist. The Hugging Face historical dataset card describes a mixed-source construction from Kaggle fake-news datasets and records split counts, while also showing unresolved licensing information. This is not a signed acquisition record for the local CSV files.

The local `data/Fake.csv` and `data/True.csv` are ignored rather than Git-tracked. Prior local audits recorded their sizes, row counts, and SHA-256 values and found consistency with the repository's local provenance record. Those values were not independently authenticated by this public-source investigation and cannot establish origin. No public record inspected here connected the local bytes to a specific upstream release, commit, acquisition date, or signed publisher checksum.

**Answer:** the dataset source is partially identified but not independently verified for the local files.

## Artifact-reference findings

No independently authenticated artifact digest, signed manifest, build attestation, or preserved reference predictions were verified. The public project profile is project-association evidence only. The inaccessible project release pages cannot be treated as evidence of absence, but until their metadata and trust mechanism are independently verified they cannot close the blocker.

No evidence was found that binds all of the following in one authenticated record:

- source revision;
- dataset identity, version, and digest;
- dependency environment;
- preprocessing and calibration configuration;
- exact production ensemble inventory; and
- artifact hashes or a trusted reference output set.

## Evidence classification

| Evidence item | Classification | Basis |
|---|---|---|
| Project owner/project association | AUTHORITATIVE BUT NOT CRYPTOGRAPHICALLY AUTHENTICATED | Public GitHub profile and repository description are visible, but do not sign the bundle. |
| Local Git history and unsigned tag | CONSISTENCY EVIDENCE ONLY | Identifies local revisions and the tag target; no verified signing key or signed tag. |
| Public GitHub release metadata | UNAVAILABLE | Exact release pages were not retrievable in this audit; absence is not inferred. |
| Hugging Face dataset metadata | AUTHORITATIVE BUT NOT CRYPTOGRAPHICALLY AUTHENTICATED | Public owner, history, split metadata, and dataset-card statements are visible; no authenticated mapping to local CSV bytes. |
| Kaggle dataset metadata | AUTHORITATIVE BUT NOT CRYPTOGRAPHICALLY AUTHENTICATED | Public version/file metadata is visible; no authenticated local-file mapping or signed digest was verified. |
| Local dataset hashes and row counts | CONSISTENCY EVIDENCE ONLY | Match local records, but the records and files share the same unauthenticated trust boundary. |
| Local artifact manifest/hash records | CONSISTENCY EVIDENCE ONLY | Hashes can detect accidental change but do not authenticate origin when the manifest source is replaceable. |
| Trusted functional or byte-identical reference | UNAVAILABLE | No independently authenticated reference predictions or artifact hashes were found. |

## Recovery-feasibility answers

1. **Can the historical bundle's origin be authenticated?** No. The evidence found does not establish an independent trust root for the bundle.
2. **Can a trusted reference establish functional or byte-identical reproduction?** No. No independently authenticated reference outputs or hashes were verified.
3. **Can the dataset source be independently verified?** Only at the level of public source identification. The local-file-to-release mapping and source authenticity remain unresolved.
4. **What minimum evidence is missing?** At minimum: an independently verified release trust root; a signed manifest or equivalent attestation covering every artifact; a source-revision binding; authenticated dataset acquisition/version/digest records; the locked build environment and commands; and trusted reference outputs or hashes if historical equivalence is claimed.
5. **Is there a concrete recovery route?** Yes, but it requires project-owner or organization action: obtain archived release metadata and signature/attestation through an independently authenticated channel, verify the signer and source revision, then verify the complete bundle without deserialization. If that evidence cannot be recovered, ask the owner to authorize a distinctly new controlled release. A new release would establish provenance for the new bundle, not retroactively authenticate the old one.

## Remaining blockers and recommended next action

The production release remains blocked. Do not activate the current local bundle based on local hashes, the unsigned tag, or a manifest downloaded from the same source as the artifacts.

Recommended next action, in order:

1. Ask the project owner or organization release authority for an independently authenticated copy of the historical release manifest/signature or build attestation, the signer trust-root record, and the release-to-source/dataset/build mapping.
2. If those records cannot be recovered, obtain explicit owner authorization for a new release and perform a controlled rebuild in a separate namespace using verified inputs, a locked environment, a signed manifest, pre-deserialization verification, compatibility tests, and rollback-safe activation.
3. Treat historical functional and byte-identical equivalence as unavailable unless an independent reference is supplied.

## Exact local files and revisions inspected or relied upon

The following local paths were read or relied upon from this audit and the preceding local evidence; no production model file was opened:

- `download_models.py`
- `download_data.py`
- `requirements.txt`
- `.gitignore`
- `phase2_calibration.py`
- `predictor.py`
- `evaluation_results/phase2_calibration_report.json`
- `evaluation_results/trusted_provenance_audit_2026-10-21/TRUSTED_PROVENANCE_AUDIT.md`
- `evaluation_results/model_reproducibility_release_plan_2026-10-21/MODEL_REPRODUCIBILITY_AND_RELEASE_PLAN.md`
- `evaluation_results/configuration_rebuild_readiness_2026-10-21/CONFIGURATION_AND_REBUILD_READINESS.md`
- `evaluation_results/historical_evidence_trace_2026-10-21/HISTORICAL_EVIDENCE_TRACE.md`
- `evaluation_results/owner_decision_package_2026-10-21/OWNER_DECISION_AND_PROVENANCE_REQUEST.md`
- Git revisions `0ddbd3498e3c06a791efb34a3f37c9181eb6a08b`, `353c20f241d73f7e875508b1eb22eafc6943f9bb`, `efb475ef5460cb720006fc8abc1dee58a041d165`, and current HEAD `8c41ae005f4bee178a2b0104cb29049f00182081`.

Public read-only queries inspected the project GitHub profile/repository/release/tag/workflow URLs, the Hugging Face dataset page and historical commit, the Kaggle dataset page, and GitHub's release/tag documentation. The exact URLs are listed above.

## Audit integrity and Git status

Before the audit/report write:

- HEAD: `8c41ae005f4bee178a2b0104cb29049f00182081`
- Branch: `main`
- Pre-existing modified files: `README.md`, `app.py`, `download_models.py`, `frontend/style.css`, `predictor.py`, `routers/api.py`.
- Pre-existing untracked files/directories included earlier audit reports and project changes.

After the audit/report write, the only new path created by this task is:

`evaluation_results/historical_release_recovery_2026-10-21/HISTORICAL_RELEASE_RECOVERY_AUDIT.md`

All other pre-existing modifications and untracked paths were preserved. No existing report, application file, artifact file, Git tag, or Git history was modified.

## Safety confirmation and limitations

- No production pickle/joblib/model binary was downloaded, loaded, deserialized, replaced, or modified.
- No model was trained or retrained.
- No dependency was installed and no language model was downloaded.
- No credentials, private keys, or secrets were requested or used.
- No remote script or workflow was executed.
- Public-source retrieval was partially limited by cache misses on exact GitHub project pages. Those misses are recorded as unavailable evidence, not as proof that corresponding records do not exist.

**Status:** historical release recovery not established; release blocker retained.
