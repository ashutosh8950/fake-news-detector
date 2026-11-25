# Task 41 — Rights-Clearance Action Plan

## Current decision

Zenodo v1.1 remains a research lead, not a cleared source. The Task 40 college and public-website gates remain `BLOCKED_INSUFFICIENT_EVIDENCE`. The record verifies version, creator, DOI, named assets, displayed file metadata, and a dataset-level CC BY 4.0 assertion. It does not verify that the creator controls all included article and third-party rights or grant every intended downstream use.

## Evidence states

Verified from the record: v1.1, publication date, creator/affiliation, DOI, package description, asset names, displayed MD5 values, and the stated CC BY 4.0 dataset label.

Only asserted by the record: that the package is a labeled fake/disinformation-versus-true news dataset and that the creator’s license assertion covers the dataset package. This is not a verified source-to-article rights chain.

Unresolved: article publishers/authors, collection authority, transformations, exact schema and labels, privacy/takedown duties, and permissions for academic demonstration, public hosting, commercial use, trained-model distribution, and raw-data redistribution.

## Action sequence

1. Owner records intended uses and authorizes rights clarification only.
2. Send the unsent request in `TASK41_RIGHTS_HOLDER_REQUEST_DRAFT.md` through an appropriate human-controlled channel; do not send it from this repository.
3. Preserve any response, license, provenance statement, source mapping, and rights exclusions as auditable records.
4. A qualified reviewer assesses whether each answer covers the specific material and use; one affirmative answer must not be generalized to other uses.
5. Owner decides whether evidence is sufficient for each checklist item.
6. If cleared, separately authorize acquisition. Record exact version, asset bytes, local cryptographic hashes, retrieval date, and transformations.
7. Re-run schema, grouping, partition, environment, secure-preflight, and release gates for the acquired input.

No step above authorizes training, artifact creation, release, hosting, or deployment.

## Track-specific blockers

College demonstration remains blocked until the owner approves the academic scope and rights evidence covers the exact dataset material, training/evaluation, attribution, and demonstration context. Public accessibility is not implied by academic clearance.

Public website remains blocked until rights evidence separately addresses inference hosting, intended commercial status, model distribution or hosted-only operation, privacy/takedown, third-party content, security, monitoring, release approval, and deployment authorization.

## Responsible parties

- Dataset creator or rights holder: provide provenance and rights evidence.
- Qualified legal/rights reviewer: assess scope and third-party limitations.
- Project owner: choose intended uses and approve or reject each gate.
- Technical release owner: verify hashes, configuration, environment, and secure preflight after any authorized acquisition.

## Stop conditions

Keep the candidate blocked if the respondent cannot establish authority, the license scope is compilation-only or unclear, article rights are excluded, intended use is not expressly covered, evidence is unsigned/unverifiable, source mapping is missing, or any owner decision is pending.
