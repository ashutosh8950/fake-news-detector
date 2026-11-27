# Task 53 — FakeNewsNet PolitiFact Feasibility and Rights Assessment

**Assessment date:** 2026-10-27
**Scope:** read-only public-document research; no acquisition or implementation

## Executive conclusion

**Status: `POTENTIALLY VIABLE — FURTHER RIGHTS REVIEW REQUIRED`.**

FakeNewsNet’s PolitiFact subset is a credible research lead for a separately assessed article-level veracity track. The official repository exposes `politifact_fake.csv` and `politifact_real.csv`, and the paper describes FakeNewsNet as combining news content, social context, and temporal information. That is closer to Track A than source-reliability or claim-only candidates.

It is **not currently approved or ready for TruthScan’s public website**. The official repository says the complete dataset cannot be distributed because of Twitter privacy policies and news-publisher copyrights. Its minimal files contain identifiers, URLs, titles, and tweet IDs—not a retained, immutable corpus of article text. PolitiFact’s own terms state that site content is for personal, non-commercial use, prohibit storing or archiving a significant portion or creating a database, and require specific written consent for uses not provided in the agreement. These records create a rights blocker for full-text retention, training, public inference, commercial use, and model-weight release until a qualified review and written permissions resolve the exact scope.

This is an assessment of feasibility, not a legal opinion and not authorization to acquire, train, publish, or deploy.

## Evidence status

### Independently checked facts

- The official repository identifies a current/up-to-date version and an `old-version` branch, but the reviewed pages did not establish an immutable release tag or revision that could be bound to a future local copy.
- The minimal repository dataset contains four CSVs, including `politifact_fake.csv` and `politifact_real.csv`, with `id`, `url`, `title`, and tab-separated `tweet_ids` fields.
- The repository states that the complete dataset cannot be distributed because of Twitter privacy policies and news-publisher copyrights. It describes collection code for news articles and social data and requires Twitter API keys for Twitter collection.
- The original paper describes FakeNewsNet as a repository containing news content, social context, and dynamic information, and identifies PolitiFact and GossipCop as distinct domains.
- PolitiFact’s terms identify The Poynter Institute as the owner of site content, restrict copying and significant archiving/database creation, limit site content to personal non-commercial use, and invite requests for material use by email.

### Not established by the reviewed evidence

- The exact mapping from PolitiFact’s rating system to the repository’s binary `fake`/`real` files, including adjudication and treatment of intermediate ratings.
- A complete, immutable release manifest and a source-to-local hash mapping for any future acquisition.
- Permission to retain or redistribute PolitiFact article text, other publisher content, images, social posts, or user metadata.
- Permission for model training, public inference on visitor text, commercial use, or distribution of trained weights.
- That a future local corpus assembled from URLs would be complete, stable, reproducible, or legally authorized.

## Dataset and label suitability

| Question | Finding | Status |
|---|---|---|
| Dataset identity | FakeNewsNet research repository; PolitiFact subset is represented by separate fake/real metadata files. | Verified from official repository |
| Exact release | Repository says to use the current version and identifies an `old-version` branch; no immutable revision was established in this review. | Partially supported |
| Unit of data | Minimal files represent news items with IDs, URLs, titles, and tweet IDs. The full collection structure includes article and social dimensions. | Verified from official repository |
| Label meaning | File names and paper context support a binary research grouping associated with PolitiFact ground truths. The exact rating-to-binary rule was not established. | Partially supported |
| Article text | Not included in the minimal CSV schema. The repository provides collection code for article content, subject to publisher/site access. | Verified from official repository |
| Track A fit | Potentially compatible with an article-level interface only if authorized article text and an approved label policy are obtained. It must not be treated as a proven general-purpose truth oracle. | Conditional inference |

The PolitiFact subset is narrower and more defensible for initial study than pooling it with GossipCop, but it may overrepresent political claims, fact-checker selection, historical topics, and source patterns. A text-only model trained from it would still face substantial distribution shift on arbitrary visitor-submitted articles.

## Rights and lawful-availability assessment

| Material or activity | Evidence found | Current assessment |
|---|---|---|
| Dataset package/metadata | Official repository publishes minimal metadata files, but the inspected pages did not state a dataset license granting all downstream uses. | `BLOCKED — RIGHTS REVIEW REQUIRED` |
| PolitiFact text and fact-check content | PolitiFact terms identify Poynter ownership and restrict significant copying, archiving/database creation, modification, and non-personal/non-commercial use absent specific consent. | `BLOCKED — RIGHTS REVIEW REQUIRED` |
| Other publisher articles | FakeNewsNet explicitly cites news-publisher copyright as a reason complete data cannot be distributed. | `BLOCKED — RIGHTS REVIEW REQUIRED` |
| Social/Twitter data | Repository says social/user information is not distributed because of Twitter policy and requires API keys for collection. | `BLOCKED — RIGHTS REVIEW REQUIRED` |
| Full-text acquisition and retention | No project-specific permission or immutable source snapshot was found. URL access alone would not establish retention rights. | `BLOCKED — RIGHTS REVIEW REQUIRED` |
| Training/internal evaluation | No reviewed source grants TruthScan this scope for the exact retained material. | `BLOCKED — RIGHTS REVIEW REQUIRED` |
| Public inference | No reviewed source authorizes a public website accepting visitor text or use of a resulting model for that purpose. | `BLOCKED — RIGHTS REVIEW REQUIRED` |
| Commercial use | PolitiFact terms state personal, non-commercial use; no broader permission was found. | `BLOCKED — RIGHTS REVIEW REQUIRED` |
| Model-weight distribution | No permission covering weights derived from retained third-party content was found. | `BLOCKED — RIGHTS REVIEW REQUIRED` |

This table does not determine legality. It identifies that the available evidence is insufficient for the proposed uses and that qualified rights review or written permission is required.

## Practical feasibility without acquiring data

The technical path is feasible in principle but not presently reproducible or authorized:

1. The minimal metadata could define an inventory and preserve IDs/URLs/titles, but it does not supply a stable article-text corpus.
2. Reconstructing text would depend on external publisher pages and the repository’s collection code. URLs can change, disappear, redirect, require access, or serve revised content, so a later reconstruction may not match the historical item.
3. A defensible build would need an approved immutable release or manifest, a permitted text-retention route, field-level rights records, deterministic transformation logs, and hashes binding approved source bytes to derived files.
4. Evaluation is feasible in principle with publisher/source-grouped splits, duplicate and near-duplicate detection, time-aware validation/test sets, training-only preprocessing, and metrics beyond accuracy. It cannot be performed responsibly until the approved corpus and label policy exist.

If full text is not authorized, FakeNewsNet could remain a metadata/research reference or support a different, explicitly approved task. It should not be converted into an article-text Fake/Real training set by assumption.

## Public website implications

Even with rights resolved, a PolitiFact-derived model would not establish truth for arbitrary visitor articles. Important risks include political and historical domain shift, unseen publishers, changed topics, unsupported languages/formats, duplicated or syndicated stories, source/label confounding, and selection bias from fact-check coverage. The product would need abstention and uncertainty handling, clear non-definitive wording, privacy/retention controls for submitted text, abuse limits, and a visible distinction between a model prediction and a verified fact.

The current fail-closed Track A behavior must remain in place. Track B’s `SUPPORTED`, `REFUTED`, and `INSUFFICIENT_EVIDENCE` synthetic prototype remains a separate track and is not a substitute for article-level training data.

## Single smallest next step

The owner should make one explicit decision: **authorize or decline a research-only, candidate-specific rights/provenance inquiry for one identified FakeNewsNet PolitiFact revision**. If authorized, the inquiry should seek a written, source-specific answer covering:

- the exact revision and fields permitted for retention;
- whether PolitiFact/publisher material may be used for training and internal evaluation;
- whether derived model weights may be distributed;
- whether a public, non-commercial or commercial inference demo is permitted; and
- attribution, notices, deletion/refresh, and redistribution requirements.

No acquisition should occur until that decision and the required rights evidence are recorded. If the answer is negative or cannot be obtained, retain FakeNewsNet only as a research lead and keep the application unavailable for inference.

## Recommendation

Keep FakeNewsNet PolitiFact as **a research lead, not an approved replacement**. It is potentially viable for a narrowly scoped academic investigation, but it is not currently viable for the intended public article-submission website because full-text availability, exact release identity, downstream rights, model-use scope, and public-hosting authorization remain unresolved.

