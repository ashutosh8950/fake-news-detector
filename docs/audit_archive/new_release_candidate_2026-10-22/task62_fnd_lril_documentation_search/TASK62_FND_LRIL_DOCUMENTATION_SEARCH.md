# Task 62 — FND-LRIL Associated Documentation Search

**Search date:** 2026-10-27  
**Scope:** public documentation and search indexes only; no acquisition or dataset inspection

## Executive summary

The official [FND-LRIL Mendeley Data record](https://data.mendeley.com/datasets/ggd7fdsr99/1) remains the only source located that explicitly names FND-LRIL. It identifies Version 1, DOI `10.17632/ggd7fdsr99.1`, contributor Shubhi Bansal, seven under-resourced Indic languages, 28,062 instances, and a declared CC BY 4.0 license.

The search also found a 2024 arXiv paper by Shubhi Bansal and coauthors describing a related but differently named **MMIFND** corpus. That paper provides useful technical leads: seven Indic languages, web collection from named Indian news sources, binary fake/real labels, 28,085 articles, preprocessing, and image requirements. However, the paper does not name FND-LRIL, its reported count differs from FND-LRIL’s 28,062 instances, and no source-to-release mapping was found. It cannot be treated as documentation of the FND-LRIL Version 1 release without further evidence.

No exact FND-LRIL paper, official repository, detailed release manifest, provenance record, or rights statement covering underlying content and TruthScan’s intended public website was located during this bounded search. This is an evidence gap, not proof that such material does not exist.

**Conclusion: `INSUFFICIENT EVIDENCE`.** FND-LRIL remains a possible research lead, but the available documentation does not justify acquisition, training, evaluation, public inference, model-weight distribution, or data redistribution. The next safe step is owner-authorized documentation review of any supplied associated paper or release materials, without downloading the dataset.

## Sources searched and exact URLs

All pages below were accessed on **2026-10-27**. Public-page access does not authenticate local files or grant permission to use dataset content.

| Source | Type | What was checked | Result |
|---|---|---|---|
| [FND-LRIL — Mendeley Data](https://data.mendeley.com/datasets/ggd7fdsr99/1) | Official dataset record | Exact title, DOI, version, contributor, description, license declaration, page metadata | Direct FND-LRIL evidence; limited technical and rights detail |
| [MMCFND / MMIFND arXiv abstract](https://arxiv.org/abs/2410.10407) | Author-associated publication record | Title, authors, submission date, abstract, dataset name and count | Direct evidence for a related MMIFND paper, not proof it is FND-LRIL |
| [MMCFND / MMIFND arXiv HTML](https://arxiv.org/html/2410.10407) | Full publisher-hosted paper text | Data collection, sources, labels, preprocessing, languages, count, task definition | Detailed associated-paper evidence; release identity mismatch remains |
| [Mendeley Data terms](https://www.mendeley.com/terms/) | Platform terms | Platform/content-rights context | Does not grant rights in underlying FND-LRIL content |
| [Task 61 review](../task61_fnd_lril_rights_review/TASK61_FND_LRIL_RIGHTS_AND_PROVENANCE_REVIEW.md) | Existing repository report | Prior gaps and bounded-search baseline | Inherited project evidence, not an external authority |

Search-index queries used included `FND-LRIL`, `ggd7fdsr99`, `Shubhi Bansal fake news corpus seven Indic languages`, `MMCFND dataset official repository`, and `FND-LRIL MMIFND`. Search results were treated as leads only; claims were included as verified only after opening the relevant page.

## Findings by research question

### 1. Exact identity and whether associated sources refer to the same release

**Directly verified:** The Mendeley record names FND-LRIL, Version 1, DOI `10.17632/ggd7fdsr99.1`, publication date 5 August 2026, and contributor Shubhi Bansal. It describes 28,062 instances in seven under-resourced Indic languages.

**Directly verified for the associated paper:** The arXiv paper is titled *MMCFND: Multimodal Multilingual Caption-aware Fake News Detection for Low-resource Indic Languages*, was submitted 14 October 2024, and names Shubhi Bansal among four authors. It describes an MMIFND dataset with 28,085 instances in seven Indic languages.

**Identity limitation:** The public sources do not state that FND-LRIL is an update, text-only subset, corrected version, or release of MMIFND. The different name, date, and count prevent treating them as the same dataset. A release manifest or author-maintained mapping would be required.

### 2. Label semantics and assignment

**Directly verified for MMIFND paper only:** The paper defines a binary function where `0` means fake news and `1` means real news. It says labels were assigned to collected news articles for classification.

**Not verified for FND-LRIL:** The Mendeley record does not state whether FND-LRIL uses the same binary definition, how labels were assigned, whether labels came from fact-checkers or source rules, how conflicts were adjudicated, or whether they were validated. The MMIFND paper’s label description cannot be transferred to FND-LRIL without a documented identity link.

### 3. Record unit, sources, collection, dates, languages

**Directly verified for MMIFND paper only:** The paper models multimodal news articles with text and visual components. It says web scraping collected articles from BoomLive, The Indian Express, IndiaTV, News18, and Vishvas News, using Selenium for dynamic pages. It reports 28,085 articles across Hindi, Bengali, Marathi, Malayalam, Tamil, Gujarati, and Punjabi. It describes extracting text, images, publication dates, tags, and keywords, excluding articles without accompanying images, and translating Indic text into English for the FLAVA model.

**Not verified for FND-LRIL:** The Mendeley record does not identify source outlets, collection dates, date range, whether records are complete articles, or whether the seven-language and label characteristics match the MMIFND paper. The associated paper is therefore a technical lead, not a provenance record for FND-LRIL.

### 4. Release methodology and reproducibility

The Mendeley record supplies a DOI and Version 1 label but does not expose a source-to-release acquisition chain, transformation log, split manifest, duplicate policy, or file digests in the inspected page.

The MMIFND paper describes collection and preprocessing at a methodological level, including scraping, cleaning, image filtering, and translation. It does not provide a verified mapping to the FND-LRIL DOI or a complete immutable release manifest for the candidate under review. It also reports a count of 28,085 rather than 28,062.

Accordingly, reproducible reconstruction of FND-LRIL cannot be established from the sources found.

### 5. Rights and license information

**Directly verified:** The FND-LRIL Mendeley record displays `CC BY 4.0`. The arXiv page identifies a CC BY 4.0 license for the paper page, not necessarily for the dataset or underlying articles.

**Not located:** No FND-LRIL-specific statement was found addressing publisher or author rights in article text, image rights, archive copies, scraping permissions, retention, preprocessing, model training, internal evaluation, public inference, commercial use, model-weight distribution, or raw/transformed-data redistribution.

The MMIFND paper’s description of web scraping and named sources is evidence about reported methodology, not permission. A dataset-level declaration must not be treated as blanket authorization for third-party content or every downstream use.

## Evidence and confidence table

| Finding | Evidence | Confidence | Limitation |
|---|---|---|---|
| FND-LRIL public identity exists | Official Mendeley record | High | Does not authenticate any local copy |
| FND-LRIL Version 1 / 28,062 / seven Indic languages | Official Mendeley record | High for the record | No per-language or source breakdown |
| FND-LRIL declares CC BY 4.0 | Official Mendeley record | High as a recorded declaration | Scope over third-party material is unresolved |
| Related MMIFND paper exists | arXiv abstract and HTML | High | It names MMIFND, not FND-LRIL |
| MMIFND technical method and sources | arXiv HTML, sections IV-A1 and IV-A2 | High for that paper | No release mapping to FND-LRIL |
| FND-LRIL uses MMIFND’s labels and sources | Inference from same contributor and seven-language overlap | Low / unresolved | Different name, date, and count; no explicit linkage |
| FND-LRIL has reproducible splits and hashes | Not found in inspected official pages | Unresolved | May exist in unlocated supplementary material |
| FND-LRIL permits TruthScan public inference | Not found | Unresolved | Requires scope-specific rights evidence/review |

## Remaining evidence gaps

| Gap | Why it matters | Minimum evidence needed |
|---|---|---|
| Exact FND-LRIL paper or technical documentation | Defines labels, fields, source identity, and methodology | Publisher/institutional paper or official supplement explicitly naming FND-LRIL DOI/version |
| Mapping between FND-LRIL and MMIFND | Prevents conflating two releases | Maintainer-authored release note or manifest explaining the 28,062 vs 28,085 difference |
| Source and acquisition provenance | Establishes what content is in the release and how it was obtained | Source inventory, dates, acquisition method, and authenticated release record |
| Label assignment and validation | Determines whether labels represent article veracity | Annotation policy, fact-checking basis, adjudication, and quality checks |
| Exact schema and record unit | Determines compatibility with Track A | Field-level schema identifying full article text, excerpts, headlines, URLs, images, and metadata |
| Reproducible release integrity | Enables repeatable research | Immutable file list, checksums, split manifest, and transformation record |
| Underlying content rights | Dataset license may not cover publisher material | Rights statement or qualified review addressing articles, images, URLs, and archives |
| Intended downstream use | Public website scope exceeds offline research | Explicit terms or permission covering training, public inference, commercial use, weights, retention, and redistribution |
| Evaluation controls | Prevents misleading accuracy claims | Documented duplicate, source, language, topic, and temporal split policy |

## Technical suitability assessment

The associated MMIFND paper demonstrates that a related research corpus can support a binary fake/real task and has a clearly described multimodal article formulation. However, this does not establish that FND-LRIL is a text-only or article-complete release suitable for the current Track A interface.

Potential risks, stated as review requirements rather than measured properties, include:

- source-label confounding if fake and real examples come from different outlet or fact-checking channels;
- duplicates or near duplicates across languages, translations, or related articles;
- temporal and topic drift in a corpus collected from particular periods and political sources;
- translation artifacts if the associated MMIFND methodology is relevant;
- image-availability selection bias if the candidate descends from the multimodal corpus;
- language imbalance hidden by the phrase “nearly balanced.”

No rows were inspected and no evaluation was run, so none of these risks is quantified here.

## Minimum gate before acquisition or model work

Before any dataset acquisition, training, evaluation, inference, or artifact work can be considered, the owner and qualified reviewer should require:

1. an owner-selected intended-use scope;
2. an authoritative FND-LRIL document explicitly defining labels, record units, sources, dates, and languages;
3. a written mapping—or explicit separation—between FND-LRIL and MMIFND;
4. immutable release files, hashes, schema, splits, and transformation history;
5. rights evidence covering underlying articles, images, and metadata;
6. explicit or qualified review of training, evaluation, retention, public inference, commercial use, model weights, and redistribution;
7. an approved leakage-aware evaluation protocol;
8. approved dependency and artifact trust-root controls.

## Safe next step

Ask the owner whether to authorize a further documentation-only review using any paper, supplement, or release note they can legitimately provide. The review should stop if the material does not explicitly identify FND-LRIL or reconcile it with MMIFND. No dataset should be downloaded, and no Task 56 inquiry should be sent without separate owner authorization.

## Validation and restrictions

- Task 61 was verified to exist and was read before this search.
- Public pages and search indexes were accessed read-only on 2026-10-27.
- No dataset, archive, article text, model artifact, package, or private account was accessed.
- No training, calibration, evaluation, inference, deployment, or application workflow was run.
- No application, dataset, model, dependency, configuration, or release-gate file was modified.
- Git HEAD and status were checked before and after; `git diff --check` was run after writing this report.
- Browser or dataset-row inspection was not performed.

## Final conclusion

`INSUFFICIENT EVIDENCE`

The search improved the technical understanding of a related MMIFND publication but did not authenticate that publication as FND-LRIL documentation. The candidate remains a research lead only. The exact release’s label semantics, provenance, reproducibility, underlying-content rights, and intended downstream permissions remain unresolved.
