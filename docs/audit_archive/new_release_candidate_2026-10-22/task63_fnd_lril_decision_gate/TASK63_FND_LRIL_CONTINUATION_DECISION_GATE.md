# Task 63 — FND-LRIL Continuation Decision Gate

**Gate date:** 2026-10-27  
**Decision state:** `PENDING OWNER DECISION`  
**Current public-release state:** `NO-GO`

## Purpose

This record converts the Task 60–62 findings into a decision point about whether FND-LRIL should receive more documentation-only attention. It does not approve the dataset, infer owner authorization, or change any release gate.

## Evidence established

The official [FND-LRIL Mendeley record](https://data.mendeley.com/datasets/ggd7fdsr99/1) identifies Version 1, DOI `10.17632/ggd7fdsr99.1`, contributor Shubhi Bansal, seven under-resourced Indic languages, 28,062 instances, and a declared CC BY 4.0 license.

Task 62 also found a related 2024 [MMCFND/MMIFND paper](https://arxiv.org/html/2410.10407) by the same contributor. It reports a differently named 28,085-item multimodal corpus and describes sources, web collection, binary labels, and preprocessing. The paper does not identify FND-LRIL, and the count, name, and release timing differ. It therefore cannot be used to upgrade FND-LRIL’s evidence status.

The current evidence supports only this limited statement: FND-LRIL is a plausible research lead for multilingual fake-news classification. It does not establish that the repository’s existing files correspond to FND-LRIL or that the dataset is authorized for any TruthScan use.

## Evidence still missing

- an authoritative FND-LRIL paper or technical release document;
- explicit label definitions, assignment method, validation, and adjudication;
- record unit and schema, including whether complete article text is included;
- source publishers, acquisition method, collection dates, and transformation history;
- a release manifest, file hashes, split definitions, and duplicate-handling policy;
- an explicit mapping to—or separation from—the MMIFND release;
- rights evidence for underlying articles, images, metadata, archives, and URLs;
- scope-specific review of retention, preprocessing, training, evaluation, public inference, commercial use, model weights, and redistribution;
- owner-selected intended-use scope and accountable rights/release reviewer.

## Risks to the intended public article-submission website

Even if the missing evidence were supplied, the candidate could still present language, publisher, topic, temporal, and formatting distribution shift. Source-label shortcuts, duplicate articles or translations, and unavailable or changed source pages could distort evaluation. A benchmark prediction would not establish factual truth for a visitor-submitted article. Privacy, retention, abuse, monitoring, abstention, and user-facing limitation controls would also remain separate release requirements.

## Owner decision

The owner should select exactly one option. Until an explicit response is supplied, the state remains **`PENDING OWNER DECISION`**.

### Option A — Continue

Authorize one narrowly scoped, documentation-only search for authoritative FND-LRIL release materials, such as a paper, supplement, schema, manifest, or maintainer-published provenance record.

**Boundary:** This option authorizes only public-documentation review. It does not authorize dataset acquisition, article-text inspection, training, evaluation, model loading, package installation, external contact, deployment, or publication.

**Success condition:** A source explicitly identifying FND-LRIL Version 1 resolves the identity, label, provenance, reproducibility, and rights questions sufficiently for a later owner decision. If it does not, the candidate remains blocked.

### Option B — Hold

Pause FND-LRIL investigation pending new authoritative evidence supplied through an approved channel.

**Boundary:** No further FND-LRIL research is started. Existing safe work may continue, including synthetic Track B tests, model-free readiness checks, UI error-state work, and documentation maintenance. This option does not approve acquisition or reject the dataset.

### Option C — Reject

Stop considering FND-LRIL as a TruthScan candidate because the current project does not want to pursue the unresolved evidence path.

**Boundary:** This is a project-selection decision, not a finding that FND-LRIL is inherently unusable or unlawful. It does not authorize a replacement dataset or any model work; a different candidate would require its own owner-approved review.

## Common prohibition for all options

No option in this gate authorizes:

- dataset acquisition or download;
- inspection or processing of dataset rows or article text;
- training, fine-tuning, calibration, evaluation, or inference;
- loading historical or new model artifacts;
- package installation or dependency changes;
- contacting authors, publishers, rights holders, or other external parties;
- deployment, publication, commit, push, tag, or release.

The Task 56 inquiry remains unsent. Track B remains synthetic-only and separate from Track A.

## Release decision

Maintain **`NO-GO` for public Fake/Real inference**. The current public-release blockers remain unresolved, including dataset rights and provenance, trusted artifact provenance, reproducible dependencies, authorized leakage-aware evaluation, security/privacy/operations controls, and final release authorization. The related MMIFND paper does not clear any of these gates.

## Decision record

| Item | Owner response | Status |
|---|---|---|
| FND-LRIL path: Continue, Hold, or Reject | Not supplied | `PENDING OWNER DECISION` |
| Intended-use scope | Not supplied | `PENDING OWNER DECISION` |
| Accountable rights/release reviewer | Not supplied | `PENDING OWNER DECISION` |
| Public inference requirement | Not supplied | `PENDING OWNER DECISION` |
| Commercial use, model weights, and data redistribution scope | Not supplied | `PENDING OWNER DECISION` |

## Evidence basis and limitations

This gate is based on the Task 60 audit, Task 61 rights/provenance review, and Task 62 associated-documentation search. Those reports distinguish direct source observations from inherited claims and unresolved questions. No new dataset or model checks were performed for this gate. The decision request itself must not be treated as authorization.

## Validation and safety checks

- The three required Task 60–62 reports were verified to exist and were read before creating this gate.
- Git HEAD and working-tree status were checked before and after.
- `git diff --check` was run after writing this document.
- Only this Task 63 Markdown document was created.
- No datasets, article text, models, packages, external accounts, training, evaluation, inference, deployment, commits, pushes, or destructive Git operations occurred.
