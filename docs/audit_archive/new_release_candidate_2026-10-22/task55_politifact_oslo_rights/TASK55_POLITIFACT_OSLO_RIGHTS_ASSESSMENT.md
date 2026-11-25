# Task 55 — PolitiFact-Oslo Rights and Reproducibility Feasibility

**Assessment date:** 2026-10-27
**Scope:** public-document research only; no acquisition or implementation

## Primary status

**`BLOCKED — RIGHTS REVIEW REQUIRED`**

The PolitiFact-Oslo Corpus is a technically credible research lead for a separately assessed English article-level Fake/Real experiment. Its paper documents complete text items, expert fact-check labels, metadata, a collection procedure, and a clear binary grouping of PolitiFact ratings. However, no dataset-specific license or permission was found for retaining the underlying text, training a model, public inference on visitor-submitted articles, commercial use, model-weight distribution, or raw/transformed-data redistribution.

PolitiFact’s terms provide a possible permission route: they state that uses not specifically permitted require specific written consent and provide an email address for material-use requests. That is a **path to request review, not permission**. It does not establish authority for third-party publisher articles, source pages, or Wayback Machine copies used during corpus construction. The owner must obtain a qualified rights determination and written permissions before any acquisition or use decision.

## Evidence and corpus identity

### Independently checked

- The corpus is described in the 2023 paper by Nele Põldvere, Md Zia Uddin, and Aleena Thomas, affiliated with the University of Oslo and SINTEF Digital. The paper is published in *Information* 14(12), article 627, DOI `10.3390/info14120627`.
- The paper describes a PolitiFact-based English corpus built by extracting fact-checking metadata and links, manually selecting the linked item corresponding to the claim, and extracting complete text, title, author/poster, and date. It says corrected items were sometimes accessed through the Wayback Machine to match the fact-checked version.
- The paper reports a preliminary corpus of 2,745 texts, 428,917 words, covering January 2019 through December 2022, with 249 sources. It reports that more than 83% of texts are social media and about 14% are news/blog, with more than 80% in the False group.
- The documented broad labels combine PolitiFact ratings as follows: False = False, Mostly False, and Pants on Fire; True = True, Mostly True, and Half True. Full Flop and No Flip were excluded because of low occurrence.
- The paper describes the material as complete texts corresponding to the claims, rather than only short claims, but it is not an immutable machine-readable release manifest.
- PolitiFact’s terms identify The Poynter Institute as the owner of site content, state that content is for personal, non-commercial use, prohibit storing or archiving a significant portion or creating a database, prohibit other copying/modification/publishing uses not allowed by the terms, and direct material-use requests to `editor@politifact.com`.

### Existing repository claims, not independently re-established here

- Task 54 selected PolitiFact-Oslo as the strongest new label-fit candidate.
- The repository’s existing release-readiness documents state that acquisition, training, trusted artifact creation, and public deployment remain blocked.

## Label and Track A suitability

The label policy is explicit enough to preserve the documented meaning: it is a binary grouping of PolitiFact’s ordinal ratings, not an independently generated universal truth label. The paper describes the labels as assigned by expert journalists at PolitiFact and warns about corpus imbalance and contextual variation.

That supports a bounded academic experiment if rights are resolved. It does not support claiming that a model establishes factual truth for arbitrary visitor articles. The corpus includes social-media text and news/blog text, so a single binary model could learn text-type, source, author, event, or platform cues. The large False/True imbalance and 2019–2022 US-focused fact-check selection also limit generalization.

The existing Track A Fake/Real interface could represent the documented broad labels without silently changing their names, but only as a model prediction with abstention and prominent limitations. Track B remains separate and must not be used to reinterpret this corpus.

## Rights pathway by use

| Intended activity | Evidence | Assessment |
|---|---|---|
| Academic/internal experimentation | Paper and institutional record establish research context, not a grant of text rights. | Blocked pending rights review. |
| Retaining complete article text | Paper says complete text was extracted from linked sources; PolitiFact terms restrict significant archiving/database creation and third-party source rights are not resolved. | Blocked. |
| Model training | No dataset-specific training permission was found. Training may involve copying and retaining third-party text; scope requires qualified review and written permission. | Blocked. |
| Public inference on visitor text | No permission for a public service or model-derived use was found. | Blocked. |
| Commercial use | PolitiFact terms state personal, non-commercial use for site content. | Blocked; written permission required. |
| Model-weight distribution | No term or permission addressing weights derived from the corpus was found. | Blocked. |
| Raw/transformed-data redistribution | PolitiFact terms restrict copying, database creation, modification and publishing; no corpus license was found. | Blocked. |
| Attribution/notices | Citation and source attribution are appropriate, but attribution alone does not cure missing permissions. Exact obligations remain unresolved. | Unresolved. |

The paper’s use of linked external publishers and occasional Wayback copies creates an additional rights layer. Permission from PolitiFact alone may not cover those materials. Each retained component and intended use requires separate review.

## Reproducibility and technical feasibility

The research paper gives a reproducible description of the collection logic, but not a complete reproducible release package. The reviewed institutional and publisher pages did not identify an immutable corpus version, downloadable manifest, source-to-file hashes, retained acquisition receipt, or public license for the text.

Without authorized access, the following risks remain:

- source pages may change, disappear, redirect, or block access;
- corrected items may differ from the versions available later;
- Wayback availability and terms may vary by item;
- exact text extraction and manual inclusion decisions may not be recoverable;
- duplicate and near-duplicate controls are not documented as a release manifest;
- a future local copy cannot be authenticated to the paper merely by matching a title, URL, or approximate count.

A responsible future build would require an approved immutable snapshot or a permitted reproducible retrieval procedure, an acquisition and transformation log, file hashes, label-policy documentation, and a rights record for every retained field.

## Future evaluation design

If approved, evaluation should:

1. group splits by source/publisher and author where feasible;
2. detect exact and near duplicates before splitting;
3. use time-aware validation and test periods;
4. keep text type and source metadata out of the prediction path unless explicitly evaluated;
5. fit preprocessing only on training data;
6. report per-class precision/recall/F1, calibration, abstention coverage, and performance by text type/source;
7. test on later and unseen publishers/topics; and
8. avoid presenting cross-validation or historical benchmark scores as public-world accuracy.

## Public website suitability

The corpus is not sufficient by itself for a public website. Visitor submissions may come from unseen publishers, languages, topics, formats, and current events outside the 2019–2022 collection. The corpus’s majority social-media composition is also unlike a general article-submission interface. The application would need explicit uncertainty/abstention behavior, privacy and retention controls for submitted text, abuse protections, and wording that distinguishes model output from verified fact.

The current fail-closed model-readiness behavior should remain unchanged until rights, provenance, evaluation, artifact trust, dependency reproducibility, and public deployment authorization are separately resolved.

## Smallest next action

The owner should authorize a **rights-review request package**—without acquiring data—containing the intended scope and the exact questions below. A qualified reviewer or rights holder must answer them before any corpus download or training decision:

- May the complete PolitiFact-Oslo text and metadata be retained and transformed for academic training and internal evaluation?
- Does permission cover the linked third-party publisher material and Wayback-sourced versions, or are separate permissions required?
- May a model trained on the retained material serve visitor-submitted text publicly?
- Is commercial use permitted?
- May derived model weights, evaluation artifacts, or transformed data be distributed?
- What attribution, notices, deletion, refresh, privacy, and access restrictions apply?

Until written answers and a reproducible source package exist, PolitiFact-Oslo should remain a **research lead, not an approved replacement**.

