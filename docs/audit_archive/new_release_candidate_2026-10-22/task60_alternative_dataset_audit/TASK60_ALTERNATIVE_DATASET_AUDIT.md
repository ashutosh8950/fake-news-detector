# Task 60 — Alternative Dataset Suitability and Rights Audit

**Audit date:** 2026-10-27  
**Scope:** read-only public-documentation research; no acquisition or model work

## Executive summary

Two new Mendeley records have a better apparent label fit than the previously reviewed source-reliability and claim-verification candidates. FND-LRIL describes a nearly balanced, multilingual fake-news corpus with 28,062 instances, and the political misinformation corpus describes a text spreadsheet whose records are news items with an explicit real/fake indicator. These facts support further review only. Neither record, as inspected, establishes rights to the underlying article material or explicitly authorizes TruthScan’s intended public visitor-submission inference, commercial use, model-weight distribution, or dataset redistribution.

FakeNewsNet has useful article-level collection structure, but its official repository says the complete dataset cannot be distributed because of Twitter privacy policies and news-publisher copyrights. Its minimal files contain identifiers, URLs, titles, and tweet IDs; full article text is collected separately. That makes it unsuitable as the current public-website replacement without a separate rights and reproducibility pathway.

**Recommendation: `FURTHER REVIEW`.** Keep FND-LRIL as the leading research lead for a candidate-specific rights/provenance review, with the multilingual/multimodal corpus as a secondary lead if its intended language and multimodal scope are acceptable. This recommendation is not approval to acquire, train, publish, or deploy. The single next step is an owner decision on intended scope followed by a rights/provenance review of the selected candidate; no data should be acquired before that gate.

## Candidate comparison

| Candidate | Apparent task fit | Evidence available from official record | Rights confidence for public website | Main technical risk | Status |
|---|---|---|---|---|---|
| FND-LRIL, Mendeley Data DOI `10.17632/ggd7fdsr99.1` | Strong apparent fit for multilingual article/text fake-news classification | Record says seven under-resourced Indic languages and 28,062 instances; label methodology, fields, dates, and article-rights provenance are not stated on the inspected page | Low/ unresolved: page says CC BY 4.0 but does not separately establish rights to underlying content or public inference/model/data redistribution | Unknown collection and labeling process; language/domain shift; duplicates and splits not documented on page | `RESEARCH LEAD — NOT APPROVED` |
| Multilingual & Multimodal Text and Image Corpus for Political Misinformation, Mendeley Data DOI `10.17632/x356jrj2cz.1` | Apparent fit for text real/fake classification, with an additional image track | Record says one news item per spreadsheet row with title, source, full report, and real/fake indicator; expert labeling is stated for images, but text-label methodology and dates are not fully documented on page | Low/ unresolved: page says CC BY 4.0; underlying publisher/article/image rights and intended downstream uses are not separately established | Political-domain and multimodal selection bias; unclear annotation and split controls; possible source/format leakage | `RESEARCH LEAD — NOT APPROVED` |
| FakeNewsNet, official GitHub repository | Partial fit: PolitiFact/GossipCop fake/real collections, but full text requires collection from publishers | Official README says complete data cannot be distributed; minimal CSVs contain ID, URL, title, and tweet IDs; collection code can retrieve articles/social data | Low: publisher copyrights and Twitter privacy restrictions are explicit; no public-use permission for retained full text or weights is established | URL drift/deletion, source and platform leakage, temporal drift, inaccessible articles, social-data dependency | `BLOCKED — RIGHTS REVIEW REQUIRED` |

No candidate is approved. “Research lead” means only that a bounded evidence review may be worthwhile after owner authorization.

## Evidence-backed findings

### 1. FND-LRIL

**Verified from the official record:** The Mendeley Data page identifies “FND-LRIL,” Version 1, published 5 August 2026, DOI `10.17632/ggd7fdsr99.1`. It describes a multilingual, nearly balanced fake-news detection corpus in seven under-resourced Indic languages with 28,062 instances and lists CC BY 4.0.

**Not established by that record:** The page does not provide enough detail to authenticate the exact article/source inventory, publication date range, label assignment protocol, annotator qualifications, duplicate policy, train/test split, or source-to-release integrity manifest. It also does not state whether the included articles are author-created, licensed for redistribution by the contributor, or reproduced under terms that cover public model inference and model-weight distribution.

**Assessment:** The name and description make FND-LRIL the strongest initial label-fit lead among the candidates reviewed here. The label semantics must still be confirmed from the associated paper, release files’ documentation, and an immutable provenance record before acquisition or training. A Mendeley “CC BY 4.0” label is evidence about the dataset record’s declared license, not conclusive proof that every underlying article or publisher permits every downstream use.

### 2. Multilingual and multimodal political misinformation corpus

**Verified from the official record:** The Mendeley Data page identifies Version 1, published 25 April 2025, DOI `10.17632/x356jrj2cz.1`, with contributors affiliated with Vishwakarma Institute of Information Technology. It describes separate image and text components. It says the text is a single Excel sheet where a record is one piece of news, with title, source, full news report, and real/fake indicator columns. It states that images are organized into real and fake folders based on expert labeling and lists CC BY 4.0.

**Not established by that record:** The page does not sufficiently document how the text real/fake labels were assigned, what “real” means operationally, the publication date range, source inventory, duplicate handling, split construction, or whether rights to the full news reports and images were obtained from their original owners. It does not expressly address public inference, commercial use, model-weight distribution, or raw/transformed redistribution.

**Assessment:** This is a plausible research lead if the project intentionally supports political and multimodal data. It is not a clean drop-in replacement for a text-only Track A without confirming label semantics, filtering the modality scope, and resolving content rights. The image component increases rights and storage complexity.

### 3. FakeNewsNet

**Verified from the official repository:** The README says the complete dataset cannot be distributed because of Twitter privacy policies and news-publisher copyrights. The minimal repository files are PolitiFact/GossipCop fake/real CSVs with ID, URL, title, and tweet IDs. The repository describes separate collection options for news articles and multiple social dimensions, and states that article text is obtained from published websites through collection code. It identifies the associated 2018 FakeNewsNet paper and an `old-version` branch.

**Assessment:** FakeNewsNet’s labels and source-specific collections are relevant to fake-news research, but the official restrictions directly conflict with treating it as a readily redistributable, reproducible article corpus for a public site. A future review would need an authorized, immutable full-text snapshot and rights analysis covering publishers, social data, and the exact public inference scope. Until then it remains blocked rather than a practical replacement.

## Rights and intended-use assessment

The records reviewed declare dataset-level licenses or describe research datasets. They do not, by themselves, establish all of the following for TruthScan:

- permission to retain and process full article text and images;
- permission to train or fine-tune a model;
- permission to run public inference on arbitrary visitor submissions;
- permission for commercial use;
- permission to distribute trained weights or checkpoints;
- permission to redistribute raw or transformed data;
- attribution, notice, retention, deletion, privacy, or takedown requirements;
- authority of the record contributor to grant rights in third-party publisher content.

For FakeNewsNet, the official repository explicitly records publisher-copyright and Twitter-privacy constraints. For the two Mendeley records, the declared CC BY 4.0 label is a useful lead but does not resolve the separate rights question for embedded third-party material. These are rights-review questions, not legal conclusions.

## Scientific validity and reproducibility risks

Before any model work, the selected candidate would need a documented target definition and an authorized, immutable release. The evaluation plan should at minimum:

1. retain only fields whose rights and purpose are documented;
2. identify and remove exact and near duplicates before splitting;
3. use publisher/source-grouped splits where source identifiers exist;
4. add a time-aware holdout to expose temporal drift;
5. fit preprocessing only on training data;
6. report class balance, per-language/domain performance, calibration, abstention, and error categories;
7. test whether source, formatting, image availability, or collection process predicts the label;
8. avoid describing benchmark performance as truth verification or generalization to arbitrary visitor articles.

The official pages inspected do not provide enough information to conclude that these controls are already present for FND-LRIL or the multilingual/multimodal corpus. For FakeNewsNet, the separate publisher and social collection channels create additional source and availability confounding risks.

## Public-website implications

Even an authorized benchmark would not establish reliable predictions for arbitrary visitor submissions. A public service would face unseen publishers, new events, language and format variation, adversarial input, privacy and retention obligations, and the risk that users interpret a model output as a verified fact. Track A must keep its output as a model classification with clear uncertainty and abstention behavior; it must not be presented as source-backed fact-checking. Track B remains a separate synthetic-only claim-verification prototype and is not a substitute for article-level labels.

## Verified, inherited, and unresolved evidence

**Verified in this task:** the three official candidate pages/repository were accessed on 2026-10-27; the factual descriptions attributed above are limited to what those pages state. No dataset download or row inspection occurred.

**Inherited from repository reports:** Task 57–59 report that the existing local datasets, historical artifacts, dependency reproducibility, evaluation validity, and public-release authorization remain unresolved, and recommend a no-go state. Those reports were read as project context, not treated as fresh experimental results.

**Unresolved:** exact license scope for underlying content; source authority; immutable release and hashes; label methodology for the two new Mendeley records; full-text retention rights; intended-use permissions; leakage-resistant splits; and owner decisions about academic-only, public, commercial, weight, and data-distribution scope.

## Minimum evidence before approval

Before any candidate can be approved for acquisition or model work, the owner and qualified reviewer should require:

1. an immutable candidate release/version and authoritative provenance record;
2. a field-level inventory distinguishing author annotations, metadata, article text, images, URLs, and social data;
3. written terms or a qualified rights determination covering the chosen intended uses;
4. a reproducible source-to-local acquisition and transformation record with digests;
5. an approved package source and hash-enforced environment;
6. an owner-approved leakage-aware evaluation protocol;
7. a documented model-artifact trust root and release process;
8. security, privacy, retention, abuse, monitoring, and final deployment approval.

## Proposed next step

Do not acquire any candidate yet. Ask the owner to select the intended-use scope and whether to authorize a **candidate-specific rights/provenance review of FND-LRIL**. If authorized, that review should inspect the associated paper and official release documentation, establish label semantics and collection history, and map the declared CC BY license separately from rights in underlying articles. If those records do not answer public-inference and content-rights questions, keep the candidate blocked and do not train.

## Source register

All sources below were accessed on **2026-10-27**. Accessing a public page does not authenticate the local repository’s files or grant permission to use any dataset.

| Source | What it supports | Limitation |
|---|---|---|
| [FND-LRIL — Mendeley Data](https://data.mendeley.com/datasets/ggd7fdsr99/1) | Dataset name, Version 1, publication date, DOI, seven Indic languages, 28,062 instances, nearly balanced description, and declared CC BY 4.0 | Does not by itself establish label protocol, underlying article rights, public inference, or reproducible splits |
| [Multilingual & Multimodal Text and Image Corpus — Mendeley Data](https://data.mendeley.com/datasets/x356jrj2cz/1) | Dataset identity/version/date/DOI, text-sheet fields, image organization, political/multimodal scope, and declared CC BY 4.0 | Does not by itself establish text-label methodology, underlying content rights, or intended downstream permissions |
| [FakeNewsNet official repository](https://github.com/KaiDMML/FakeNewsNet) | Non-distribution statement, minimal CSV fields, collection requirements, article/social retrieval options, and cited paper | Repository documentation is not a permission grant for publisher or social content |
| [FakeNewsNet paper record](https://arxiv.org/abs/1809.01286) | Research publication associated with the FakeNewsNet project | A paper is not a license or authorization |
| [Task 57 blocker register](../task57_release_blocker_register/TASK57_RELEASE_BLOCKER_REGISTER.md) | Inherited project blocker and no-go context | Prior report evidence; not independently re-run in this research task |
| [Task 58 owner decision gate](../task58_owner_decision_gate/TASK58_OWNER_DECISION_GATE.md) | Pending scope/direction decisions and release gates | Does not grant approval |
| [Task 59 owner checkpoint](../task59_owner_decision_checkpoint/TASK59_OWNER_DECISION_CHECKPOINT.md) | Current hold and safe-work boundary | Does not resolve external evidence |

## Conclusion

`FURTHER REVIEW` is warranted for FND-LRIL as a research lead, not as an approved replacement. No candidate currently satisfies the evidence required for TruthScan’s intended public website. The application should remain fail-closed, and all acquisition, training, evaluation, artifact, and deployment work should remain gated on owner scope decisions and rights/provenance evidence.
