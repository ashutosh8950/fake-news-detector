# Task 35 — Dataset Evidence Unblocking Checklist

All items remain **OPEN** unless an independently verifiable record is
attached. This checklist does not authorize training or release.

## Identity and acquisition

- [ ] **REQUIRED BEFORE RELEASE TRAINING:** Identify the exact upstream source, publisher/author, version or commit, URL, acquisition date, and acquisition process.
- [ ] **REQUIRED BEFORE RELEASE TRAINING:** Retain or independently authenticate the source artifact/archive and record its SHA-256.
- [ ] **REQUIRED BEFORE RELEASE TRAINING:** Document deterministic filtering, ordering, label mapping, and generated `subject`/`date` fields.
- [ ] **REQUIRED BEFORE RELEASE TRAINING:** Reproduce or independently verify the mapping to local hashes `672ab39a75ac75fef9ecbb1a84e2936e064b44a32197a4801d9d0fb63ca9d57e` and `c3105d9266fd2ad484aad43b13801930434ffcd68894cc975128e52433a0c6ad` without using those local records as the trust root.

## Rights and intended use

- [ ] **REQUIRED BEFORE MODEL-ARTIFACT DISTRIBUTION:** Obtain version-specific license text or written permission from an authorized rights holder covering training and derived-model distribution.
- [ ] **REQUIRED BEFORE PUBLIC HOSTING:** Confirm public inference hosting scope, commercial/non-commercial restrictions, attribution, notices, privacy, takedown, and derivative-work conditions.
- [ ] **REQUIRED BEFORE DATA REDISTRIBUTION:** Separately confirm redistribution rights for the source data and embedded third-party content.
- [ ] **OWNER/LEGAL DECISION REQUIRED:** Record the intended release scope and acceptance of applicable obligations.

## Authentication and preflight binding

- [ ] Bind source revision, source digest, local-output hashes, transformation record, and intended-use scope in an authenticated evidence record.
- [ ] Provision the approval/trust root independently of the evidence being verified.
- [ ] Require the Task 30/31 preflight to reject missing, stale, unsigned, mismatched, or self-asserted evidence.
- [ ] Keep dataset eligibility blocked until the external records are supplied and independently reviewed.

## Separate gates that remain open

- [ ] Owner approval of grouping policy and exact partition manifests.
- [ ] Defensible dependency lock/environment record.
- [ ] Native filesystem/symlink coverage where required.
- [ ] Authenticated release manifest and organization-controlled signing process.
- [ ] Final deployment and rollback approval.

## Responsible parties and acceptable evidence

The project owner or release authority should supply the acquisition and scope
records. A rights holder or authorized publisher must supply permission where
the public host metadata is insufficient. Acceptable evidence should be a
versioned source record, authenticated archival copy, signed or independently
verified permission, or other auditable document whose identity and scope can
be checked without requesting credentials or private keys.

If these records cannot be recovered, authorize a different clearly licensed
dataset as a distinct new input. Do not claim that substitution authenticates
or reproduces the current local bundle.
