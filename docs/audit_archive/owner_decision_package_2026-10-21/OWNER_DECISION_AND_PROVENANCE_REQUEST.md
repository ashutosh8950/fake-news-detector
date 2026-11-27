# TruthScan Owner Decision and Trusted Provenance Request

Date: 2026-10-21 (Asia/Calcutta)

## Executive summary

TruthScan production release remains blocked. Existing audits establish source-code safeguards and a plausible rebuild procedure, but they do not establish historical model provenance or release authenticity.

Two owner decisions are required:

1. Define what the Phase 2 field production_switch means and explain its historical mismatch.
2. Choose whether to recover and authenticate the historical release, or authorize a clearly new controlled rebuild and release.

No decision or new provenance evidence has been received in this task. No production artifact was loaded, downloaded, rebuilt, modified, or retrained.

## Current evidence status

- Current HEAD: 8c41ae005f4bee178a2b0104cb29049f00182081.
- Commit 0ddbd34 introduced the Phase 2 generator and report with production_switch=false in both.
- Commit 353c20f changed the tracked report to true while removing Random Forest from the report and predictor; the generator continued writing false.
- No historical code consumes production_switch. Current predictor.py selects five models and averages their calibrated class-1 probabilities independently of the field.
- Local dataset hashes match local provenance records, but upstream publisher, version, and acquisition record are not authenticated.
- requirements.txt is not a complete dependency lock; environment_versions.json is a snapshot, not an authenticated build specification.
- No trusted reference predictions, independently authenticated artifact hashes, signed manifest, or release attestation was found.

The existing release verdict is unchanged: production loading and deployment approval remain blocked.

## Decision 1 — Meaning of production_switch

The project owner must decide which description is authoritative:

### Option 1A — Historical promotion metadata

production_switch=true in the report records that a five-model report was promoted or approved for production after the Random Forest removal. The owner should identify the promotion decision, date, reviewer, source revision, and corresponding artifact build. This would explain why the report changed in commit 353c20f while the generator still emitted false.

Consequence: the field remains historical metadata only unless the owner explicitly defines an operational contract. It must not be treated as proof that the artifacts were authenticated.

### Option 1B — Experimental or non-production metadata

The report was an evaluation or experiment record and true was written accidentally or by a separate process. The owner should identify the correct intended value, the generating process, and whether the report metrics remain valid for the five-model ensemble.

Consequence: the report cannot be used as an authoritative production approval record until corrected or superseded by a reviewed, separately identified report.

### Option 1C — Obsolete field

The field has no intended meaning and should be retired from future release metadata. The owner should document that decision and identify the authoritative production-selection record instead.

Consequence: historical reports remain unchanged for audit purposes; future releases use explicit release identity and approval metadata.

### Required answer and evidence

Please answer:

- What did production_switch represent in the Phase 2 workflow?
- Why did commit 353c20f change the report to true while the generator remained false?
- Was the report intended to describe the actual production five-model ensemble, an experiment, or another configuration?
- Which source revision, command, run record, or approval record supports the answer?

The current inference code does not consume this field. No code change should be made merely to force the values to agree before the owner establishes the intended meaning.

## Decision 2 — Authority for rebuild and release

The owner must authorize one of these routes.

### Option 2A — Recover and authenticate the historical release

Supply or identify an owner-controlled record that binds the existing bundle to:

- the exact source revision;
- dataset identity and upstream revision;
- dependency/runtime environment;
- build and calibration commands;
- complete artifact inventory and trusted digests;
- a signed manifest or independently authenticated release attestation.

Consequence: if complete evidence is supplied and verified, the historical bundle may be evaluated for compatibility and release approval. Signing existing files after the fact does not prove their historical origin.

### Option 2B — Authorize a new controlled release

Authorize a rebuild in a new, non-production namespace using newly verified inputs and a controlled environment. Record new source, dataset, dependency, configuration, calibration, evaluation, manifest, and release-authentication evidence.

Consequence: the result is a new release. It must not be represented as proof that the existing historical bundle was authentic, nor as byte-identical reproduction unless an independently trusted reference proves that.

### Required authorization

The owner should identify the person or organization authorized to approve the route, the intended release identity, and the approval scope. The request is for evidence and decisions only; it does not request private keys, passwords, credentials, or secrets.

## Evidence request checklist

### 1. Dataset identity and source

| Requested evidence | Classification | Dependency/status |
|---|---|---|
| Original dataset name, publisher, upstream URL, version/revision, acquisition date, and license | REQUIRED BEFORE REBUILD | Required to identify the training inputs; currently unresolved. |
| Independently trusted dataset hashes, sizes, schema, row counts, and label mapping | REQUIRED BEFORE REBUILD | Must be authenticated independently of local evaluation records. |
| Acquisition log or source-release record connecting local Fake.csv and True.csv to the upstream source | REQUIRED BEFORE REBUILD | Needed to bind local bytes to a source; absent today. |
| Existing local v1/v2/v3 source_provenance.json records | OPTIONAL HISTORICAL EVIDENCE | Useful consistency records, but not independent authenticity. |

### 2. Training and calibration procedure

| Requested evidence | Classification | Dependency/status |
|---|---|---|
| Exact source revision used for the historical or new build | REQUIRED BEFORE REBUILD | Must be recorded before running a controlled build. |
| Exact training and calibration commands, working-directory assumptions, and output paths | REQUIRED BEFORE REBUILD | Needed for procedural reproducibility. |
| Vectorizer, preprocessing, estimator, split, seed, fold, and calibration configuration | REQUIRED BEFORE REBUILD | Current scripts document much of this; the executed historical configuration is not authenticated. |
| Explanation of intended model-selection behavior and five-model versus six-model transition | OWNER DECISION REQUIRED | Needed to interpret commit 353c20f and avoid silently substituting a workflow. |
| Historical run logs or build report | OPTIONAL HISTORICAL EVIDENCE | Helpful for historical provenance; not currently present as an authenticated record. |

### 3. Dependency and environment

| Requested evidence | Classification | Dependency/status |
|---|---|---|
| Exact Python version and platform/container identity | REQUIRED BEFORE REBUILD | Current records show Python 3.11.9 in one environment, but no authenticated build identity. |
| Fully resolved dependency lock with hashes where practical | REQUIRED BEFORE REBUILD | requirements.txt is not sufficient; no lock exists. |
| Exact scikit-learn, NumPy, SciPy, pandas, joblib, spaCy, and application dependency versions | REQUIRED BEFORE REBUILD | v3 snapshot records versions but does not authenticate them. |
| en_core_web_sm version, acquisition source, and checksum | REQUIRED BEFORE REBUILD | Current documentation names the model; its identity/checksum is not independently recorded. |
| Existing Docker/CI/Render install commands | OPTIONAL HISTORICAL EVIDENCE | They show current installation procedure but do not provide a locked environment. |

### 4. Trusted reference outputs

| Requested evidence | Classification | Dependency/status |
|---|---|---|
| Independently trusted reference bundle or reference prediction/probability corpus | REQUIRED BEFORE RELEASE | Needed for functional-equivalence testing; none found. |
| Reference test inputs, expected labels, per-model probabilities, and ensemble probabilities | REQUIRED BEFORE RELEASE | Tolerances must be defined before comparison; none available. |
| Independently authenticated artifact hashes for every required file | REQUIRED BEFORE RELEASE | Needed for byte-identical testing; local hashes are not sufficient. |
| Existing evaluation metrics and phase reports | OPTIONAL HISTORICAL EVIDENCE | They document observed results but are not trusted references to model bytes. |

### 5. Model bundle and production ensemble

| Requested evidence | Classification | Dependency/status |
|---|---|---|
| Authoritative list of required artifacts and excluded legacy files | REQUIRED BEFORE REBUILD | Current source defines five active models; local directory also contains unused Random Forest. |
| Model class labels, probability interface, feature dimensions, and calibration metadata | REQUIRED BEFORE RELEASE | Must be validated against trusted real artifacts; no trusted real-artifact test has passed. |
| Explanation of whether phase2_calibration_report.json is historical, experimental, or production-approved | OWNER DECISION REQUIRED | Directly depends on Decision 1. |
| Historical model inventory and build output record | OPTIONAL HISTORICAL EVIDENCE | Could connect files to a run, but no authenticated record was found. |

### 6. Release trust root and authentication

| Requested evidence | Classification | Dependency/status |
|---|---|---|
| Independent trust root and authorized signing identity | REQUIRED BEFORE RELEASE | Must be verified through an owner-controlled channel separate from artifact hosting. |
| Signed manifest or independently authenticated release attestation | REQUIRED BEFORE RELEASE | Must bind release ID, source revision, and every artifact digest. |
| Verification procedure executed before deserialization | REQUIRED BEFORE RELEASE | Must reject missing, malformed, unsigned, or mismatched bundles. |
| Key rotation, revocation, and compromised-key response process | REQUIRED BEFORE RELEASE | Needed for ongoing release trust. |
| Public key material stored beside the manifest only | NOT SUFFICIENT | An attacker able to replace both files could replace the trust root. |

### 7. Owner identity and authorization

| Requested evidence | Classification | Dependency/status |
|---|---|---|
| Named authorized owner/release approver and scope of authority | OWNER DECISION REQUIRED | Needed to approve the historical or new-release route. |
| Written approval for a new release identity and release criteria | OWNER DECISION REQUIRED | Required before release work begins. |
| Private keys, passwords, tokens, or credentials | NOT REQUESTED | Future signing must use an organization-controlled process; secrets must not be pasted into the repository or an AI chat. |

## Evidence dependencies

1. Decision 1 is required before treating any report field as release metadata.
2. Dataset identity, source revision, dependency lock, preprocessing configuration, and calibration procedure are required before an acceptance-grade rebuild.
3. A trusted reference is required before functional-equivalence or byte-identical acceptance can be claimed.
4. A trust root and signed manifest/attestation are required before release authenticity can be claimed.
5. Functional validation, byte identity, and release authenticity are separate gates. A successful new build cannot automatically pass any of the other gates.
6. Owner authorization is required before choosing the historical-recovery route or creating a new release identity.

## Acceptance gates and closure criteria

### Gate 1 — Rebuild readiness

Pass only when the owner decision is recorded, exact inputs and source revision are identified, environment dependencies are locked, output namespace is isolated, and the build procedure is reviewed. Current status: **BLOCKED**.

### Gate 2 — Procedural reproducibility

Pass only when a clean environment can execute the recorded commands and produce the documented artifact set and report schema without touching production files. Current status: **NOT ESTABLISHED**.

### Gate 3 — Functional validation

Pass only when trusted reference inputs and predefined prediction/probability tolerances are available, and the rebuilt bundle passes class-label, probability, feature-dimension, calibration-metadata, preprocessing, and ensemble tests. Current status: **UNAVAILABLE; no trusted reference exists**.

### Gate 4 — Byte-identical reproduction

Apply only if an independently trusted historical reference exists. Compare all required artifact bytes against trusted reference hashes. A match establishes equality to that reference; it does not independently establish the reference’s historical origin. Current status: **UNAVAILABLE**.

### Gate 5 — Release authenticity and artifact verification

Pass only when a trust root is independently verified, the signed manifest or attestation binds the exact source/release and artifact hashes, verification happens before deserialization, the complete bundle passes compatibility checks, and activation/rollback evidence is retained. Current status: **BLOCKED**.

### Gate 6 — Production deployment authorization

Pass only after the preceding gates pass and an authorized owner approves deployment, including rollback, resource, readiness, and audit evidence. Current status: **NOT GRANTED**.

## Release-blocker closure criteria

The current release blocker can be closed only when:

- production_switch semantics are documented by the owner;
- historical or new-release route is authorized;
- required dataset and environment evidence is supplied;
- procedural rebuild criteria pass;
- trusted functional reference exists or functional equivalence is explicitly marked unavailable for a new release;
- byte-identical status is explicitly marked unavailable unless trusted reference hashes exist;
- release trust root and signed manifest/attestation verify independently;
- compatibility, staging, rollback, deployment, and audit gates pass;
- production approval is separately recorded.

## Copy-ready request to the project owner

Please provide a written decision on the following before TruthScan production artifacts are rebuilt or released:

1. What did production_switch represent in the Phase 2 workflow, and why did commit 353c20f change the tracked report to true while the generator continued writing false? Please identify the authoritative source revision, command, run record, or approval record supporting the answer. The current predictor does not consume this field.
2. Which route is authorized: (a) recover and independently authenticate the historical bundle and its provenance, or (b) authorize a controlled rebuild as a new release? If route (b) is chosen, please confirm that it will not be described as proof of the historical bundle’s origin or byte-identical reproduction without a trusted reference.
3. Please supply evidence, not secrets: dataset publisher/source/version/acquisition/license and trusted hashes; source revision and build commands; exact dependency/runtime and spaCy language-model versions; calibration and model-selection configuration; trusted reference predictions or hashes where available; authoritative bundle inventory; and the independent trust-root/signed-manifest or attestation process.

Do not send private signing keys, passwords, tokens, or credentials. Future signing should use an organization-controlled release process.

## Previous audit reports supporting this request

- evaluation_results/trusted_provenance_audit_2026-10-21/TRUSTED_PROVENANCE_AUDIT.md — established that the manifest is not independently authenticated and reviewed the verifier boundary.
- evaluation_results/model_reproducibility_release_plan_2026-10-21/MODEL_REPRODUCIBILITY_AND_RELEASE_PLAN.md — assessed partial rebuildability and missing historical inputs/environment lock.
- evaluation_results/configuration_rebuild_readiness_2026-10-21/CONFIGURATION_AND_REBUILD_READINESS.md — classified production_switch as conflicting and acceptance-grade rebuild as blocked.
- evaluation_results/historical_evidence_trace_2026-10-21/HISTORICAL_EVIDENCE_TRACE.md — traced the report-only change in commit 353c20f and found no trusted release evidence.

## What remains unknown

- The intended historical meaning of production_switch.
- Why the report was changed independently of the generator.
- The authenticated upstream identity and revision of the local dataset.
- The exact historical source revision, command, environment, and build record for the current model files.
- A trusted reference bundle, predictions, and artifact hashes.
- An independently verified release trust root and signed manifest/attestation.

These are unknown because repository history and local reports provide consistency and chronology, but no independently authenticated owner record. They must not be filled by inference from metrics, filenames, timestamps, local hashes, or unsigned release metadata.

## Recommended next action

Send the copy-ready request to the authorized project owner. Do not begin a production rebuild. After the owner responds:

1. Record Decision 1 and Decision 2.
2. Validate the supplied evidence against the acceptance gates.
3. If historical evidence is recoverable, authenticate it and assess the existing bundle.
4. Otherwise, authorize and plan a new isolated release with newly recorded provenance and independent release authentication.

## Verification record

### Before writing

- HEAD: 8c41ae005f4bee178a2b0104cb29049f00182081.
- Branch: main.
- Existing modified and untracked files were recorded and preserved.
- Target directory did not exist.

### After writing

- HEAD remains 8c41ae005f4bee178a2b0104cb29049f00182081.
- Existing working-tree changes and prior reports remain preserved.
- Only new documentation created by this task: evaluation_results/owner_decision_package_2026-10-21/OWNER_DECISION_AND_PROVENANCE_REQUEST.md.
- No existing file was modified by this task.
- No production artifact was loaded, downloaded, rebuilt, modified, or retrained.

