# TruthScan Task 51 — NELA-GT Candidate-Specific Readiness Assessment

Assessment date: 2026-10-26  
Scope: read-only research; no dataset acquisition, row inspection, model work, or application changes.

## Executive conclusion

**Current Track A decision: `NOT SUITABLE FOR CURRENT TRACK A`.**

NELA-GT is an article collection with source-level reliability and credibility annotations. Its documented labels do not establish whether each individual article is factually true or false. Converting source reliability into TruthScan's `Fake`/`Real` labels would change the target and could create source memorization and label leakage. No such conversion is recommended or approved here.

**Separate source-reliability decision: potentially suitable after specified changes.**

NELA-GT could support a separately named research task such as predicting source-level reliability or studying article language conditional on source reliability. That task would require an owner-approved target definition, source-grouped evaluation, rights review, and a release scope that does not imply article-level fact verification.

No NELA-GT release is approved for acquisition, training, public inference, model distribution, or redistribution.

## Exact candidate identity

NELA-GT is a family of dated releases, not one unqualified dataset. The official repository currently documents NELA-GT-2018, 2019, 2020, 2021, and 2022-related material. The repository README identifies NELA-GT-2020 usage examples and lists release metadata for 2020–2022, including SQLite and JSON formats. It does not by itself establish which release should be used for TruthScan.

The existing TruthScan records refer to NELA-GT-2020/2021/2022 as research candidates, but do not establish an authenticated acquisition or select one exact release. The owner must select one release before any future acquisition or technical assessment.

## What the sources establish

The NELA-GT-2018 paper describes approximately 713,000 articles collected from 194 outlets during February–November 2018 and source ratings from multiple assessment sites. The NELA-GT-2019 paper describes approximately 1.12 million articles from 260 sources collected during 2019. The NELA-GT-2020 paper describes nearly 1.8 million articles from 519 sources collected during 2020 and source-level labels from Media Bias/Fact Check.

The official repository README describes article fields including date, source, title, content, author, publication and collection timestamps, and URL. It describes aggregated source labels as `Reliable`, `Unreliable`, `Mixed`, and `Null` for the documented releases. It also states that collected article text may be copyrighted and is transformed to make it unsuitable for ordinary news consumption while retaining utility for text analysis.

These facts establish dataset structure and intended research context. They do not establish a license for all underlying article text, metadata, embedded tweets, public hosting, commercial use, model-weight distribution, or raw/transformed-data redistribution.

## Track A suitability: article-level Fake/Real

### Why the existing contract is not supported

The documented target is attached to the source/outlet, while the TruthScan Track A API presents an article-level `Fake`/`Real` prediction. A reliable outlet can publish an incorrect article and an unreliable outlet can publish a correct one. Therefore, assigning every article the outlet's label would be a proxy-label transformation, not a validated article-truth ground truth.

The following risks would remain even for research:

- **Source memorization:** random article splits can allow the model to learn outlet identity instead of article-level signals.
- **Label leakage:** source identifiers, URLs, domains, author fields, timestamps, or formatting can reveal the source label.
- **Within-source variation:** one outlet-level label cannot represent every article.
- **Temporal drift:** source ratings and editorial behavior can change over time.
- **Assessment dependence:** labels inherit the coverage, methodology, and biases of the external rating sources.
- **Domain mismatch:** NELA-GT is a news-landscape/source-reliability resource, not a directly equivalent replacement for the current local Fake/Real corpus.

The current recommendation is therefore not to train Track A on NELA-GT or to relabel it into `Fake`/`Real`.

## Separate source-reliability task

NELA-GT is more defensible for a redesigned task whose target is explicitly one of:

- source-level reliability classification;
- source-level multi-dimensional credibility analysis; or
- article-language analysis conditioned on a source-level reliability annotation.

This would require a separate API and UI contract. It must not reuse Track A's `Fake`/`Real` wording, and results must not be described as factual verdicts about an article.

### Required changes before technical work

1. Select one exact dated release and record its official identifier, archive identity, revision/date, and intended fields.
2. Obtain and review the exact source terms and any data-provider conditions.
3. Determine whether the transformed article text, metadata, URLs, and embedded tweets may be stored, processed, displayed, used for training, and used in a public demo.
4. Define the target label and whether the task is binary, three-class, or multi-label. Do not collapse labels without owner and scientific review.
5. Decide whether article text, source identifiers, URLs, authors, dates, and embedded-tweet fields are in scope; document leakage controls for every included field.
6. Define a separate product name and response contract for source reliability.

## Proposed future evaluation design

This is a proposal only; no data was acquired or evaluated.

- Split by publisher/source group so articles from the same source do not cross train, validation, and test partitions.
- Add duplicate and near-duplicate detection across titles, body text, URLs, and syndicated content.
- Use time-aware validation and a final temporal test set to measure drift.
- Fit preprocessing and feature selection only on the training partition.
- Run source-held-out tests to measure whether the model generalizes beyond seen outlets.
- Report per-class precision, recall, F1, macro-F1, balanced accuracy, calibration, and abstention/coverage where applicable.
- Compare against a source-only baseline and a text-only baseline. A strong source-only baseline would expose shortcut learning.
- Report source, date, language, topic, and label coverage limitations rather than presenting a single accuracy score as fact-checking performance.
- Keep any public demonstration explicitly labelled as source-reliability research.

## Rights and intended-use assessment

### Evidence currently available

- The official NELA repository states that collected articles may be copyrighted.
- The repository describes a text transformation intended to reduce ordinary news consumption.
- The repository provides citation guidance and release metadata.

### Evidence still missing

The reviewed materials do not establish, for a selected exact release:

- a broad license covering the underlying article text and metadata;
- permission for internal or external training;
- permission to distribute trained weights;
- permission to host public inference;
- permission for commercial use;
- permission to redistribute raw or transformed data;
- treatment of embedded tweets and third-party material;
- retention, deletion, takedown, attribution, and notice obligations.

These are unresolved rights questions, not legal conclusions. A qualified rights reviewer should assess the exact release and proposed use.

## Owner decision checklist

- [ ] Select an exact NELA-GT release, or decline NELA-GT.
- [ ] Decide whether the target is source reliability, article analysis conditioned on source labels, or another explicitly defined task.
- [ ] Confirm that Track A's article-level Fake/Real contract will not be relabeled from source-level annotations.
- [ ] Define academic-only, public-inference, commercial, model-distribution, and raw/transformed-data redistribution scope separately.
- [ ] Assign an accountable rights/provenance reviewer.
- [ ] Obtain exact release terms and review underlying article, metadata, URL, and embedded-tweet rights.
- [ ] Approve source-grouped, duplicate-resistant, time-aware evaluation rules.
- [ ] Approve a separate UI/API name and limitation statement if a source-reliability prototype proceeds.
- [ ] Keep acquisition, training, artifact creation, and deployment blocked until the above decisions and evidence are recorded.

## Source register

Access date for the external sources below: **2026-10-26**. These sources were inspected as public documentation only; no dataset file or row was downloaded or read.

| Source | What it supports | What it does not establish |
|---|---|---|
| [MELALab NELA-GT repository](https://github.com/MELALab/nela-gt) | Release metadata, formats, article fields, source-level labels, text transformation and copyright warning | A blanket downstream license, rights to every article/metadata item, public hosting or model distribution permission |
| [NELA-GT-2018 paper](https://arxiv.org/abs/1904.01546) | 2018 collection scope, outlet count, source-rating methodology and research purpose | Article-level truth labels or permission for the current project's intended uses |
| [NELA-GT-2019 paper](https://arxiv.org/abs/2003.08444) | 2019 release scope and source-level ground-truth description | A license for underlying content or approval for Track A relabeling |
| [NELA-GT-2020 paper](https://arxiv.org/abs/2102.04567) | 2020 release scope, source count and source-level MBFC labels | Article-level truth, public deployment permission or model-weight rights |
| [NELA-GT-2018 publication record](https://ojs.aaai.org/index.php/ICWSM/article/view/3261) | Publication identity, authors, venue and DOI | Dataset acquisition identity for this repository |

## Existing repository evidence

The following local records were reviewed:

- `REPLACEMENT_DATASET_ASSESSMENT.md`
- `DATASET_PROVENANCE_DECISION.md`
- `MODEL_RELEASE_PREREQUISITES.md`
- `FEVER_DECISION_READINESS.md`
- Task 27 provenance records
- Task 37–42 replacement-dataset reports where referenced by the existing assessment

The local records consistently classify NELA-GT as a research lead rather than an approved replacement. They also state that the existing `Fake.csv`/`True.csv` provenance, historical model trust root, dependency reproducibility, and public deployment authorization remain unresolved.

## Boundary and final status

This assessment did not authorize acquisition, processing, training, evaluation, model loading, artifact creation, public hosting, or deployment. Track B remains synthetic-only and separate from Track A.

**Final status:** `NOT SUITABLE FOR CURRENT TRACK A`

Separate source-reliability work is **potentially suitable after specified changes**, owner approval, exact-release selection, rights review, and a new evaluation/API contract.
