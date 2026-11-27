# Task 38 — Fakeddit Rights Review

## Evidence status

**Overall Fakeddit status: `CONDITIONAL_PENDING_CONFIRMATION` for research-only
consideration; `BLOCKED_INSUFFICIENT_EVIDENCE` for model distribution, public
hosting, commercial use, or raw-data redistribution.** Fakeddit is not approved
or authorized for acquisition.

Retrieval date for the public sources below: **2026-10-22**.

## What the official record establishes

- The [official Fakeddit repository](https://github.com/entitize/Fakeddit) and
  [project page](https://fakeddit.netlify.app/) identify a multimodal fake-news
  benchmark with more than one million samples and provide public project
  documentation.
- The [official README](https://github.com/entitize/Fakeddit/blob/master/README.md?plain=1)
  documents v2.0 text/metadata downloads, separate image and comment sources,
  a public released test set, and usage guidance. It says paper results use
  multimodal samples and identifies a `clean_title` field for filtered text.
- The [original paper](https://arxiv.org/abs/1911.03854) describes the dataset
  as Reddit-derived and multimodal, with fine-grained fake-news categories.
- No dataset license was found in the reviewed official repository README or
  project page. The absence of a license is recorded as unresolved, not as
  proof that no license exists.

## Platform and third-party rights

Reddit’s [Public Content Policy](https://support.reddithelp.com/hc/en-us/articles/26410290525844-Public-Content-Policy),
updated 2026-10-06, says public content can be used for non-commercial uses
such as learning and community, while commercial purposes require discussion
with Reddit. It describes licensing arrangements, deletion handling, and
restrictions on deleted/private content and sensitive profiling. This is a
platform policy, not a Fakeddit dataset license or a grant from every Reddit
author, image owner, or linked publisher.

The official Fakeddit documentation separately identifies text, metadata,
comments, images, and image URLs. Terms for one component cannot be assumed to
cover all others. User-generated comments, image files, linked media, deleted
content, and publisher material require component-level review.

## Activity classification

| Activity | Status | Evidence-supported conclusion |
|---|---|---|
| Internal research/training/evaluation | `CONDITIONAL_PENDING_CONFIRMATION` | Official research documentation and Reddit’s noncommercial research language support further review, but exact dataset terms, deletion handling, and component rights remain unresolved. |
| Commercial use | `BLOCKED_INSUFFICIENT_EVIDENCE` | Reddit’s policy says commercial purposes require discussion/licensing; no project-specific commercial permission was found. |
| Trained-model artifact distribution | `BLOCKED_INSUFFICIENT_EVIDENCE` | No Fakeddit term grants derived-model distribution; model scope and user-content obligations require review. |
| Public inference hosting | `BLOCKED_INSUFFICIENT_EVIDENCE` | No Fakeddit or Reddit record reviewed authorizes the proposed hosting scope, especially commercial hosting. |
| Raw dataset redistribution | `BLOCKED_INSUFFICIENT_EVIDENCE` | The project provides download instructions, but no verified dataset license or blanket right to redistribute Reddit and third-party content was found. |

No activity is marked `SUPPORTED_BY_VERIFIED_EVIDENCE`. No activity is marked
`PROHIBITED_BY_DOCUMENTED_TERMS` for the exact Fakeddit v2.0 package because its
dataset-specific terms were not established; the platform policy creates
material conditions and unresolved questions.

## Questions requiring confirmation

1. What license and revision-specific terms attach to the v2.0 text/metadata,
   comments, images, and test files?
2. How are deletions, user requests, private/quarantined content, and retention
   handled in the released files?
3. Does the project have authority to redistribute the content and authorize
   derived model artifacts or public hosting?
4. Does the owner want a text-only task, and if so which fields are permitted?
5. Are commercial use, public hosting, and raw-data redistribution covered by
   written permission or an applicable license?

Until answered, Fakeddit remains a research lead only.
