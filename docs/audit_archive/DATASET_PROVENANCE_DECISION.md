# TruthScan Dataset Provenance Decision Record

Status: **OWNER DECISION PENDING**. The existing dataset remains `NO-GO` / `BLOCKED_INSUFFICIENT_EVIDENCE` for release work. This record compares two options; it does not authorize acquisition, processing, training, evaluation, artifact creation, hosting, or deployment.

## Current evidence

The Task 27 provenance report verifies local file metadata and SHA-256 values; the schema, labels, row counts, and consistency information are recorded or carried forward from prior provenance records. These records establish consistency with prior local records, but they do not authenticate the mapping between the current local `Fake.csv` and `True.csv` bytes and an authoritative upstream source. Task 27 also states that no authenticated acquisition record, exact upstream revision, source digest, transformation receipt, license snapshot, chain-of-custody record, or rights-holder permission was recovered.

The acquisition script documents possible Hugging Face and Kaggle sources, but it does not prove which source produced the current local bytes. Public dataset pages and matching filenames or row counts are not authenticated source-to-file mappings and do not establish authority over third-party news content.

The Task 37–42 packages found no approved replacement dataset. FEVER, NELA-GT, LIAR, Fakeddit, CoAID, FakeNewsNet, and the Zenodo v1.1 lead remain research candidates or blocked options with unresolved rights, task-fit, downstream-use, or provenance questions. The Zenodo record’s displayed CC BY 4.0 label does not by itself clear underlying article rights, public hosting, model distribution, commercial use, or raw-data redistribution.

The current application correctly remains fail-closed. Existing model artifacts and release roots are not independently authenticated, and the dependency lock is exact-version pinned but not hash-pinned or clean-install verified.

## Option A — Recover existing dataset provenance and rights

### Evidence required

An owner-authorized recovery effort must obtain, and independently authenticate where possible:

- exact upstream publisher, dataset name, revision/commit or release, URL, and acquisition date;
- original source artifact or authenticated archival copy with a source SHA-256 digest;
- acquisition command/process and custody record;
- deterministic transformation receipt showing filtering, ordering, relabeling, and generated fields used to produce the exact local `Fake.csv` and `True.csv` bytes;
- independently verified mapping to the recorded local hashes in the Task 27 checklist;
- version-specific license or written permission from a party authorized to grant it;
- explicit scope for training/internal evaluation, trained-model distribution, public inference hosting, commercial use if relevant, and raw or transformed-data redistribution if relevant;
- treatment of third-party article text, publisher rights, privacy, deletion, takedown, attribution, and notice obligations;
- owner/legal-review decision recording the permitted scope and exclusions.

### What Option A could unblock

If all evidence is recovered and accepted, Option A could establish whether the existing files are eligible inputs for a separately approved controlled rebuild. It could also establish which downstream uses are permitted, subject to separate technical and release gates.

### What Option A would not automatically unblock

It would not by itself:

- authenticate the historical model pickles;
- establish a reproducible dependency/build environment;
- approve grouping policy, duplicate handling, or leakage-resistant partitions;
- prove that the historical 98.44% result generalizes;
- create a trusted artifact manifest or release root;
- authorize training, artifact distribution, public hosting, or deployment.

### Main unresolved risks

- The historical acquisition event may be unrecoverable.
- A public source license may not cover embedded third-party article content.
- The current local bytes may have been transformed, reordered, filtered, or assembled from more than one source.
- Historical model artifacts may not have been built from these exact bytes or this exact source revision.

## Option B — Authorize assessment of a replacement dataset

### Evidence and review required before selection

The owner must first authorize research or acquisition assessment for a named candidate. For each candidate, the review must establish:

- official creator/publisher identity and canonical source;
- exact version, revision, file identity, and reproducible acquisition metadata;
- license or written permission attached to the exact dataset material, not merely a repository or compilation label;
- provenance of underlying articles, claims, headlines, images, comments, metadata, or other third-party material;
- permissions separately assessed for training/evaluation, academic demonstration, public inference, commercial use, trained-model distribution, and raw/transformed-data redistribution;
- attribution, share-alike, noncommercial, privacy, deletion, takedown, platform, and notice obligations;
- task suitability: article-level versus claim-level content, label semantics, language/topic scope, source cues, duplicate risks, and required preprocessing;
- owner-approved grouping, partition, evaluation, and intended-use scope.

The Task 42 evidence package specifically records that no reviewed candidate is approved for the public website. FEVER may be considered only as a separate claim-verification demonstration, not as a direct replacement for the article-level Fake/Real task. NELA-GT, Zenodo v1.1, LIAR, and other candidates retain documented rights or suitability gaps.

### What Option B could unblock

If a candidate passes the evidence review and the owner authorizes acquisition, Option B could create a new provenance boundary for a future, separately versioned evaluation and controlled model build. It would not establish equivalence to the historical TruthScan model or dataset.

### What Option B would not automatically unblock

It would not automatically authorize:

- downloading or processing the candidate;
- training, calibration, or evaluation;
- public inference or commercial use;
- distribution of trained artifacts or raw data;
- reuse of the existing model, metrics, labels, API contract, or split methodology without review;
- production deployment or release.

### Main unresolved risks

- A dataset-level open license may not cover embedded third-party content.
- Claim-verification labels may not map to Fake/Real article labels.
- Source or publisher cues may create leakage or shortcut-learning risks.
- Candidate licensing may permit research use but not public hosting or model distribution.
- A replacement requires new technical, provenance, evaluation, and release evidence.

## Comparison

| Area | Option A: existing dataset recovery | Option B: replacement assessment |
|---|---|---|
| Immediate owner action | Authorize provenance/rights recovery and name responsible reviewer | Authorize research/assessment of a named candidate or candidate set |
| Required identity evidence | Original source revision, acquisition record, transformation receipt, source and local digest mapping | Candidate’s official revision, acquisition metadata, local digest, and transformation record after separately authorized acquisition |
| Rights evidence | Permission covering the exact existing files and intended downstream uses | License/permission covering exact candidate material and intended downstream uses |
| Technical compatibility | Preserves current article-level Fake/Real task if identity and labels are confirmed | May require new labels, preprocessing, grouping, splits, and API/evaluation decisions |
| Historical model relationship | Could clarify whether current artifacts were built from these inputs; does not prove it alone | Cannot authenticate or reproduce the historical bundle |
| External dependency | Original publisher, uploader, rights holder, or project records; qualified review | Candidate creator/publisher and qualified review; possibly platform or third-party rights holders |
| Current status | `NO-GO`, blocked | No candidate approved; assessment itself requires owner authorization |
| What it can lead to | A separately approved rebuild using the existing task/data, if evidence succeeds | A new, explicitly versioned dataset and model path, if evidence succeeds |
| Stop condition | Missing authenticated mapping or rights scope | Missing candidate provenance, rights scope, task fit, or owner authorization |

No cost or completion-time comparison is made because the repository evidence does not support one.

## Owner decision — intentionally undecided

The owner should complete these fields outside the automated gates:

- **Option A — continue recovery of existing `Fake.csv`/`True.csv`:** `UNDECIDED`
- **Option B — authorize replacement-dataset assessment:** `UNDECIDED`
- **Responsible rights/provenance approver:** `UNASSIGNED`
- **Qualified legal or rights reviewer required:** `UNDECIDED`
- **Permitted intended uses:** `UNDECIDED` (internal academic evaluation, public inference, commercial use, model distribution, raw-data redistribution)
- **Acquisition authorized:** `NO — no explicit authorization is recorded in the reviewed evidence`
- **Training/calibration authorized:** `NO`
- **Artifact creation or distribution authorized:** `NO`
- **Deployment authorized:** `NO`

Authorizing research or assessment is not authorization to acquire, process, train, create artifacts, host inference, or deploy.

## Evidence required before any training or release work

Before any real-data training or candidate artifact generation begins, the selected path must have:

1. Owner-recorded scope and responsible approver.
2. Authenticated dataset identity, revision, acquisition record, transformation receipt, and source-to-local digest mapping.
3. Rights evidence covering the exact intended activities, including third-party content restrictions.
4. Approved label semantics, grouping policy, duplicate/leakage treatment, and exact partition manifests.
5. Reproducible target dependency/environment evidence, including spaCy model identity and checksum.
6. A reviewed source commit and a separate candidate-only build authorization.
7. Independently provisioned production trust roots and a signed or equivalently authenticated artifact manifest.
8. Reconciled evaluation evidence; the historical 98.44% claim must not be treated as release proof without resolving its provenance and relationship to the group-aware analyses.
9. Secure preflight success with all mandatory evidence bound to the exact release identity.
10. Separate approval for model distribution, public hosting, commercial use, and raw-data redistribution where applicable.

Until then, the correct behavior is the current fail-closed application state: diagnostics may run, but inference must remain unavailable when trusted artifacts are not ready.

## Evidence/recommendation distinction

The following are repository evidence: the Task 27 `BLOCKED_INSUFFICIENT_EVIDENCE` status, missing acquisition and rights records, the Task 37–42 unapproved candidate findings, the existing artifact-verification behavior, and the unresolved dependency and trust-root reports.

The two-option structure, owner-decision fields, comparison, and evidence order above are recommendations for governance and release preparation. They are not approvals, legal conclusions, or claims that any candidate is usable.

## Files examined

- `MODEL_RELEASE_PREREQUISITES.md`
- `evaluation_results/new_release_candidate_2026-10-22/task27_dataset_provenance/TASK27_DATASET_PROVENANCE_AND_LICENSE_REPORT.md`
- `evaluation_results/new_release_candidate_2026-10-22/task27_dataset_provenance/TASK27_UNBLOCKING_CHECKLIST.md`
- Task 37 owner decision and replacement research package
- Task 38 targeted LIAR/Fakeddit rights review
- Task 39 dual-track dataset selection
- Task 40 Zenodo rights verification
- Task 41 rights-clearance action plan
- Task 42 alternative dataset research
- `evaluation_results/new_release_candidate_2026-10-22/task42_alternative_dataset_research/TASK42_RECOMMENDATION_AND_GAPS.md`

No datasets, rows, models, packages, or external resources were downloaded or processed. No training, calibration, artifact loading, application-code change, gate change, commit, push, or deployment was performed.
