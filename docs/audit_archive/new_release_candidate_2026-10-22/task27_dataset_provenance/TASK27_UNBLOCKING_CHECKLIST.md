# Task 27 — Dataset Provenance and Licensing Unblocking Checklist

All items below are **OPEN** unless an independently verifiable record is attached. This checklist does not approve training or deployment.

## Identity and acquisition

- [ ] **OPEN — REQUIRED BEFORE RELEASE TRAINING:** identify the exact upstream dataset, publisher/author, version or commit, URL, acquisition date, and acquisition process.
- [ ] **OPEN — REQUIRED BEFORE RELEASE TRAINING:** retain the original downloaded source artifact or an independently authenticated archival copy and its SHA-256.
- [ ] **OPEN — REQUIRED BEFORE RELEASE TRAINING:** document the deterministic transformation from upstream data to `data/Fake.csv` and `data/True.csv`, including filtering, row ordering, label mapping, and generated `subject`/`date` fields.
- [ ] **OPEN — REQUIRED BEFORE RELEASE TRAINING:** reproduce or independently verify the mapping to the exact local hashes `672ab39a75ac75fef9ecbb1a84e2936e064b44a32197a4801d9d0fb63ca9d57e` and `c3105d9266fd2ad484aad43b13801930434ffcd68894cc975128e52433a0c6ad` without treating the local records as the trust root.

## Rights and intended use

- [ ] **OPEN — REQUIRED BEFORE RELEASE DISTRIBUTION:** obtain the version-specific license or written permission from an authorized rights holder.
- [ ] **OPEN — REQUIRED BEFORE RELEASE DISTRIBUTION:** confirm the permission covers model training and distribution of derived model artifacts.
- [ ] **OPEN — REQUIRED BEFORE PUBLIC HOSTING:** confirm public web inference, commercial/non-commercial scope, attribution, notices, takedown, privacy, and any derivative-work conditions.
- [ ] **OPEN — REQUIRED BEFORE SOURCE REDISTRIBUTION:** separately confirm that redistribution of the source data is permitted. Do not infer this from permission to train a model.
- [ ] **OPEN — OWNER/LEGAL DECISION:** record the intended release scope and acceptance of applicable restrictions.

## Technical gates that remain separate

- [ ] **OPEN — OWNER DECISION:** select and approve exactly one grouping policy and its configuration fingerprint.
- [ ] **OPEN — OWNER DECISION:** approve the exact partition manifests, hashes, and known mixed-label/leakage limitations.
- [ ] **OPEN — REQUIRED BEFORE BUILD:** pass the isolated runner’s refusal-default and path-containment checks.
- [ ] **OPEN — REQUIRED BEFORE BUILD:** resolve dependency locking and offline reconstruction gaps, including spaCy model provenance.
- [ ] **OPEN — REQUIRED BEFORE RELEASE:** create and independently authenticate a manifest and release trust root.
- [ ] **OPEN — REQUIRED BEFORE DEPLOYMENT:** complete compatibility, validation, deployment authorization, and rollback checks.

## Decision rule

Until the identity, mapping, and rights items are complete, classify the exact local datasets as `BLOCKED_INSUFFICIENT_EVIDENCE` for a controlled release. A new clearly licensed replacement dataset would require a new identity and provenance record; it must not be described as historical equivalence.

## Evidence request wording

Please provide records—not private keys or credentials—that identify the exact dataset release used to create the local CSV files, show the source-to-local transformation and digest mapping, and establish permission for the intended training, derived-model distribution, and public-hosting uses. If the source license does not cover one of those uses, provide written authorization from a party with authority to grant it or narrow the release scope and document that decision.
