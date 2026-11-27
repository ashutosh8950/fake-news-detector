# Task 38 — LIAR Rights Review

## Evidence status

**Overall LIAR status: `CONDITIONAL_PENDING_CONFIRMATION` for research-only
consideration; `BLOCKED_INSUFFICIENT_EVIDENCE` for model distribution, public
hosting, commercial use, or raw-data redistribution.** LIAR is not approved or
authorized for acquisition.

Retrieval date for the public sources below: **2026-10-22**.

## What the official record establishes

- The [official UCSB data index](https://sites.cs.ucsb.edu/~william/data/)
  exposes an archive named `liar_dataset.zip`, dated 2017-04-23 and sized about
  1.0 MB. The index does not state a license or downstream-use grant.
- The [original LIAR paper](https://arxiv.org/abs/1705.00648) describes a
  decade-long collection of 12.8K manually labeled short statements from
  PolitiFact, with truthfulness labels and source-document links.
- The [dataset documentation mirrored for LIAR](https://github.com/tfs4/liar_dataset/blob/master/README)
  states that original sources retain copyright and says the dataset is for
  research purposes only. Because this README was inspected in a third-party
  mirror rather than the official archive contents, it is treated as relevant
  documentation but not as an independently authenticated license grant.
- The [LIAR dataset card](https://huggingface.co/datasets/ucsbai/liar/blob/main/README.md)
  identifies the dataset and its PolitiFact source, but leaves licensing and
  several data-creation fields unspecified.

## Rights implications

The [PolitiFact terms and copyright page](https://politifact.com/copyright/)
states that site content is owned by The Poynter Institute, is protected by
copyright, and is for personal, non-commercial use. It also states that
storing or archiving a significant portion or creating a database is
prohibited, and that copying, modifying, publishing, transmitting, creating
derivative works, transferring, or selling content requires specific written
consent.

These terms are evidence about PolitiFact website content and a material rights
constraint. They do not, without a legal analysis of the LIAR archive and its
metadata, prove exactly which fields or uses are covered. They do establish
that public availability is not blanket permission.

## Activity classification

| Activity | Status | Evidence-supported conclusion |
|---|---|---|
| Internal research/training/evaluation | `CONDITIONAL_PENDING_CONFIRMATION` | Dataset is publicly described and research-oriented, but exact archive terms, source-content rights, and project authorization remain unresolved. |
| Commercial use | `BLOCKED_INSUFFICIENT_EVIDENCE` | No commercial permission was found; PolitiFact terms state personal, non-commercial use for site content. |
| Trained-model artifact distribution | `BLOCKED_INSUFFICIENT_EVIDENCE` | No term expressly grants derived-model distribution, and source-content rights remain unresolved. |
| Public inference hosting | `BLOCKED_INSUFFICIENT_EVIDENCE` | No hosting permission or commercial/noncommercial scope is established. |
| Raw dataset redistribution | `BLOCKED_INSUFFICIENT_EVIDENCE` | The archive has no verified redistribution license; PolitiFact terms raise database/copying restrictions. |

No activity is marked `SUPPORTED_BY_VERIFIED_EVIDENCE` or
`PROHIBITED_BY_DOCUMENTED_TERMS` for the LIAR archive as a whole. The evidence
is incomplete; the PolitiFact terms are a documented constraint on relevant
source content, not a complete adjudication of the archive.

## Technical/legal questions still requiring confirmation

1. What exact files and revision are in the official 2017 archive, and what
   license or permission applies to those files?
2. Which fields are original PolitiFact content, dataset-created labels or
   metadata, and third-party source links?
3. Does a rights holder authorize internal training, model artifact
   distribution, hosting, commercial use, and raw redistribution separately?
4. What attribution, deletion, notice, or source-link obligations apply?
5. Is a new claim-level task acceptable to the owner, rather than a binary
   article-level replacement?

Until these questions are answered by authoritative records or qualified legal
review, LIAR remains a research lead only.
