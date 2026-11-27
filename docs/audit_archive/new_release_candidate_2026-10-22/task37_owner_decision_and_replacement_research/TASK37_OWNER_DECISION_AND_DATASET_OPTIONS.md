# Task 37 — Owner Decision and Replacement-Dataset Options

## Executive summary

The existing `Fake.csv`/`True.csv` path remains **NO-GO**. Tasks 35–36
established local consistency only; they did not recover acquisition provenance,
source-to-local mapping, or rights-holder permission.

Replacement research produced four plausible research candidates, but no
candidate is currently authorized or release-cleared:

- **LIAR** is the closest structural fit for text classification, but its
  official materials do not establish a license covering model distribution,
  hosting, or raw-data redistribution.
- **Fakeddit** has clear official documentation, revisioned v2.0 download
  instructions, and a large labeled text/multimodal benchmark, but its
  repository does not establish a dataset license and the material includes
  Reddit content and third-party media.
- **CoAID** has an official repository, version history, and a research paper,
  but the repository evidence reviewed does not state a dataset license and the
  COVID-health content raises additional rights and scope questions.
- **FakeNewsNet** has detailed official provenance and collection documentation,
  but explicitly says the complete dataset cannot be distributed because of
  Twitter privacy and publisher copyright. It is not a suitable raw-data
  redistribution candidate without separate permission.

No dataset was downloaded, cloned, scraped, or processed. These are research
leads only, not approvals or recommendations to acquire immediately.

## Existing-dataset decision

Path A remains blocked. The existing local hashes are integrity/consistency
records, not source provenance or licensing evidence. To unblock Path A, the
owner must recover an authenticated acquisition record, exact source revision,
source digest, deterministic transformation receipt, and permission from a
party authorized to grant the intended uses. Existing local files must not be
replaced or relabeled as a result of this research.

## Replacement options

### LIAR — strongest narrow text benchmark lead

Official materials identify LIAR as approximately 12.8K human-labeled short
statements from PolitiFact with six truthfulness labels. The original paper is
the primary research source and an official UCSB download URL is referenced by
the research record. The reviewed official dataset-card material leaves the
licensing section unspecified; PolitiFact-originated statements and analyses
also require rights and terms review.

Suitability: useful for a new claim-level text task, but not a drop-in
replacement for the existing article-level `Fake.csv`/`True.csv` binary corpus.

### Fakeddit — strongest scale and documentation lead

The official project repository documents version 2.0 text/metadata downloads,
public train/validation/test material, and a multimodal benchmark of Reddit
submissions. The official usage instructions distinguish text, metadata,
comments, and images and note that paper results use multimodal samples.

Suitability: technically plausible for a new release only after defining a
text-only or multimodal task, group policy, Reddit-content restrictions, image
and comment handling, and a verified license/permission path.

### CoAID — domain-specific research lead

The official repository identifies a COVID-19 healthcare misinformation dataset,
reports version history from 0.1 through 0.4, and describes news, social posts,
engagements, and labels. The official README reviewed here does not state a
dataset license or model-distribution permission.

Suitability: potentially useful only for a healthcare-misinformation model;
domain shift makes it unsuitable as an assumed general replacement, and rights
for article text, social content, and public hosting require confirmation.

### FakeNewsNet — provenance-rich but distribution-constrained lead

The official repository documents collection from PolitiFact and GossipCop,
minimal CSV metadata, collection scripts, source URLs, and social-data
requirements. It also explicitly states that the complete dataset cannot be
distributed because of Twitter privacy policies and news-publisher copyrights.

Suitability: research-only or permission-dependent use may be possible, but raw
redistribution is blocked by the published restriction. API terms, article
copyright, current source availability, and model/artifact distribution remain
separate questions.

## Owner decisions required

The following fields remain undecided; no answer is inferred:

1. Continue Path A recovery for the existing dataset: **PENDING**.
2. Authorize further metadata/licensing research for Path B: **PENDING**.
3. Authorize acquisition of a selected replacement later: **PENDING**.
4. Select intended uses: internal evaluation, model distribution, public hosting,
   commercial use, and/or raw-data redistribution: **PENDING**.
5. Identify the person or organization authorized to approve rights and release:
   **PENDING**.

Authorization to research a candidate would not authorize download, acquisition,
training, or release. Any selected dataset must pass a separate provenance,
rights, grouping, environment, preflight, and release review.

## Recommended next action

Ask the owner to authorize **research-only Path B** and select one candidate for
formal rights review, with Fakeddit and LIAR as the initial comparison set. Do
not acquire either dataset until the owner identifies intended uses and a
qualified reviewer confirms the applicable terms. In parallel, keep one final
Path A recovery request open for the missing historical records.

The next implementation task should be a rights-and-provenance intake template
for the owner-selected candidate, not a training run or dataset substitution.
