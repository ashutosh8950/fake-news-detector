# Task 61 — FND-LRIL Rights and Provenance Review

**Review date:** 2026-10-27  
**Scope:** read-only public-source research; no dataset acquisition or model work

## Executive summary

FND-LRIL is a plausible research lead for multilingual fake-news classification, but the evidence reviewed here is not sufficient to establish a defensible rights or provenance pathway for TruthScan. The official Mendeley record identifies Version 1, DOI `10.17632/ggd7fdsr99.1`, a contributor, seven under-resourced Indic languages, 28,062 instances, and a declared CC BY 4.0 license. It does not establish the source publications, article-level acquisition chain, label-assignment method, date coverage, reproducible splits, or permission for retaining and redistributing underlying third-party content.

The page’s dataset-level license declaration is not treated as proof of rights in the underlying articles, nor as permission for public inference, commercial use, model-weight distribution, or raw/transformed-data redistribution. No authoritative FND-LRIL paper or detailed release documentation was located during this bounded review. The candidate therefore remains unapproved.

**Final disposition: `INSUFFICIENT EVIDENCE`.** FND-LRIL merits further consideration only after the owner selects an intended-use scope and authorizes a candidate-specific evidence request or review. No acquisition, training, evaluation, model loading, or public deployment should begin on the current record.

## Evidence table

| Research question | Evidence directly checked in Task 61 | Assessment | Status |
|---|---|---|---|
| Dataset identity | Official Mendeley record names FND-LRIL and gives DOI `10.17632/ggd7fdsr99.1` | Identity of the public record is established; correspondence to any local file is not | `DOCUMENTED` for public record; `NOT ESTABLISHED` for local files |
| Creator/maintainer | Record lists Shubhi Bansal as contributor | Contributor is identified; institutional role, maintainer responsibilities, and authority over underlying content are not established | `PARTIAL` |
| Version and release date | Version 1; published 5 August 2026 | The public record supplies a version/date, but no immutable file manifest or digest was shown on the inspected page | `PARTIAL` |
| Scope and language | Seven under-resourced Indic languages; 28,062 instances; nearly balanced description | Useful high-level scope only; language list and per-language counts are not given on the page | `PARTIAL` |
| Record type | Page calls it a fake-news detection corpus but does not describe fields or whether records are complete articles, excerpts, headlines, or links | Article-level suitability cannot be confirmed from the inspected record | `UNCLEAR` |
| Label semantics | “Fake news detection” and “nearly balanced” are stated | Operational meaning of fake/real, adjudication, annotator process, and validation are not documented on the page | `UNCLEAR` |
| Source provenance | No source/publisher inventory or acquisition history appears on the inspected page | Underlying source identity and chain of custody remain unproven | `NOT DOCUMENTED` |
| Transformation history | No transformation, cleaning, deduplication, relabeling, or split-generation record appears on the inspected page | Reproducibility cannot be assessed | `NOT DOCUMENTED` |
| Dataset-level license | Mendeley record displays CC BY 4.0 | This verifies the record’s declared license label, not the rights status of each included article or other third-party material | `DOCUMENTED` as declaration; scope `UNCLEAR` |
| Underlying article rights | No statement was found addressing publisher or author rights in the record | Dataset-package licensing does not resolve this gap | `NOT DOCUMENTED` |
| Training and internal evaluation | No intended-use statement was found on the inspected record | Requires explicit terms or qualified review | `NOT DOCUMENTED` |
| Public inference | No permission or restriction was found addressing a visitor-facing service | Requires scope-specific authorization/review | `NOT DOCUMENTED` |
| Commercial use | No statement was found | Must remain unresolved | `NOT DOCUMENTED` |
| Model-weight distribution | No statement was found | Must remain unresolved | `NOT DOCUMENTED` |
| Raw/transformed redistribution | No statement was found | Must remain unresolved | `NOT DOCUMENTED` |
| Reproducible evaluation | No documented split, duplicate policy, source grouping, or temporal protocol was found | A future protocol can be designed, but current documentation does not establish that one exists | `NOT DOCUMENTED` |

## Facts verified directly from official sources

The official [FND-LRIL Mendeley Data record](https://data.mendeley.com/datasets/ggd7fdsr99/1), accessed **2026-10-27**, states:

- name: FND-LRIL;
- Version 1;
- publication date: 5 August 2026;
- DOI: `10.17632/ggd7fdsr99.1`;
- contributor: Shubhi Bansal;
- description as a multilingual, nearly balanced fake-news corpus;
- seven under-resourced Indic languages;
- total of 28,062 instances;
- declared licence: CC BY 4.0.

The same page does not expose enough information to verify the label methodology, source inventory, date range, exact schema, full-text status, split construction, or third-party rights. The Mendeley page’s general footer also states that content rights may remain with Elsevier, licensors, and contributors, and that Creative Commons terms apply to open-access content; this reinforces the need to distinguish the record’s license declaration from rights in embedded source material.

No FND-LRIL dataset paper, official repository, detailed dataset card, license supplement, provenance manifest, or immutable file-hash record was located through the bounded public search performed for this task. This is a search limitation, not proof that no such material exists.

## Claims inherited from Task 60

Task 60 identified FND-LRIL as the strongest apparent label-fit lead among the candidates reviewed, based on the Mendeley description. Task 60 also correctly cautioned that the declared CC BY 4.0 label does not establish rights to underlying articles or public-website use. Those are inherited project findings, not treated as independently proven beyond the source inspection described above.

Task 57–59 records continue to report a `NO-GO` state for public Fake/Real inference, unresolved dataset and artifact provenance, incomplete dependency reproducibility, and pending owner decisions. This review does not change those statuses.

## Provenance and label-validity assessment

### Dataset identity and reproducibility

The DOI and Version 1 record provide a useful public identity. They do not establish that the downloadable files are immutable, that their bytes have a published digest, or that a future researcher can reconstruct the same corpus from documented upstream sources. No source-to-release mapping, acquisition date, collection method, transformation log, or local-file correspondence was documented on the inspected page.

### Labels and task fit

The phrase “fake news detection corpus” suggests an intended classification use, but it does not define the target scientifically. It remains unknown whether labels represent article truth, fact-check outcomes, source reputation, author judgment, weak supervision, or another construct. It is also unknown whether “instances” are complete articles, excerpts, headlines, or linked records. Therefore, compatibility with TruthScan’s article-level Fake/Real interface is not established.

The seven-language scope could create language-specific domain shift and uneven label quality. The page’s “nearly balanced” description is not a substitute for per-language, per-topic, per-source counts. No claims about date ranges, topic coverage, duplicates, source leakage, or temporal leakage can be made without documentation or approved data inspection.

### Future evaluation requirements

If the candidate later receives approval, a defensible evaluation would require an immutable release and a documented protocol including:

1. exact field and label definitions;
2. source and publisher inventory, where legally and operationally permissible;
3. exact and near-duplicate detection before splitting;
4. source-grouped splits to test generalization beyond memorized publishers;
5. time-aware validation and test partitions;
6. preprocessing fit only on training data;
7. per-language and per-domain metrics, calibration, abstention, and error analysis;
8. a public-submission limitation statement that does not call predictions factual verification.

No such evaluation was run in this task.

## Rights matrix

The matrix records the state of evidence, not a legal conclusion.

| Intended activity | Status | Evidence and limitation |
|---|---|---|
| Access the public dataset record | `DOCUMENTED` | Official Mendeley record is publicly accessible and identifies Version 1. This does not authorize downloading or use of the content. |
| Retain full article text | `UNCLEAR` | The inspected page does not establish whether full articles are included or whether retention rights exist. |
| Preprocess or transform records | `UNCLEAR` | No scope-specific permission or transformation terms were found. |
| Train or fine-tune a model | `UNCLEAR` | CC BY 4.0 is displayed for the dataset record, but underlying content and downstream training scope are not separately documented. |
| Internal evaluation | `UNCLEAR` | No explicit internal-evaluation statement was found. |
| Public inference on visitor submissions | `NOT DOCUMENTED` | No permission for a public service was found. Visitor text also raises separate privacy and operational obligations. |
| Commercial use | `NOT DOCUMENTED` | No commercial-use statement was found beyond the dataset-level label. |
| Distribute model weights | `NOT DOCUMENTED` | No model-weight terms were found. |
| Redistribute raw or transformed data | `NOT DOCUMENTED` | No redistribution scope, notices, takedown, or third-party-content terms were found. |
| Attribute contributors and sources | `PARTIAL` | CC BY 4.0 generally signals attribution obligations, but the required attribution and notices for all underlying content are not established from this record. |

The correct next step is rights review, not an assumption that any row or article is cleared for the intended use.

## Technical suitability

FND-LRIL merits further consideration because the official description explicitly targets fake-news detection and reports multilingual coverage. However, technical suitability is currently **unverified** because the inspected official record does not document:

- complete schema and whether full article text is present;
- label definitions and assignment/verification procedure;
- publication dates and source domains;
- exact release files and integrity digests;
- duplicate, near-duplicate, source-overlap, or temporal-split controls;
- per-language and per-class distributions;
- a reproducible train/validation/test protocol.

The candidate must not be treated as a validated replacement for `Fake.csv`/`True.csv`, and no model-performance inference may be drawn from its public description.

## Missing evidence before any gated activity

Before acquisition could be considered:

1. owner-selected intended-use scope: academic-only, public non-commercial, commercial-capable, model distribution, and data redistribution;
2. authoritative dataset documentation or paper defining labels, fields, languages, dates, sources, and collection method;
3. immutable Version 1 file manifest and hashes;
4. source-to-release and transformation records;
5. field-level rights analysis distinguishing annotations, metadata, article text, images, URLs, and third-party content;
6. explicit terms or qualified review covering training, evaluation, retention, public inference, commercial use, weights, and redistribution;
7. approved evaluation protocol addressing duplicates, sources, time, language, calibration, and abstention;
8. approved dependency source and reproducible environment;
9. artifact trust-root and release approval plan.

## Safe next step

Ask the owner whether to authorize a **documentation-only candidate review** of FND-LRIL’s associated paper and official release materials, with no download or acquisition. If the owner authorizes that review, its first acceptance criterion should be a complete evidence package for label semantics, source provenance, release integrity, and rights scope. If those records do not establish the required rights, keep FND-LRIL blocked and do not proceed to acquisition or model work.

## Validation and boundaries

- The three required prerequisite reports were verified to exist and were read before this review.
- Public official documentation was accessed read-only on 2026-10-27.
- No dataset, article text, model artifact, package, or external private resource was acquired or inspected.
- No training, calibration, evaluation, inference, deployment, or application workflow was run.
- No application, dataset, dependency, model, configuration, or release-gate file was modified.
- Git HEAD and status were checked before and after; `git diff --check` was run after creating this report.

## Source register

| Source | Access date | What it supports | Limitation |
|---|---|---|---|
| [FND-LRIL — Mendeley Data](https://data.mendeley.com/datasets/ggd7fdsr99/1) | 2026-10-27 | Identity, Version 1, date, DOI, contributor, seven Indic languages, 28,062 instances, description, declared CC BY 4.0 | Does not establish full provenance, label method, article rights, or downstream use permissions |
| [Mendeley Data terms](https://www.mendeley.com/terms/) | 2026-10-27 | Platform-level terms context and distinction between platform records and content rights | Does not grant rights in FND-LRIL’s underlying material |
| [Task 60 audit](../task60_alternative_dataset_audit/TASK60_ALTERNATIVE_DATASET_AUDIT.md) | Local record | Inherited candidate ranking and prior rights caution | Prior report; not a new external source |
| [Task 57 blocker register](../task57_release_blocker_register/TASK57_RELEASE_BLOCKER_REGISTER.md) | Local record | Inherited public-release blockers and no-go recommendation | Prior report; not a new experiment |
| [Task 58 owner decision gate](../task58_owner_decision_gate/TASK58_OWNER_DECISION_GATE.md) | Local record | Pending owner scope decisions and release gates | Does not grant approval |

## Final disposition

`INSUFFICIENT EVIDENCE`

FND-LRIL remains a possible research lead, but the current public record is insufficient to justify acquisition, training, evaluation, public inference, model-weight distribution, or data redistribution. The owner must first choose the intended scope and authorize a bounded documentation/rights review. Until the missing evidence is supplied and reviewed, TruthScan should remain fail-closed and no-go for public Fake/Real inference.
