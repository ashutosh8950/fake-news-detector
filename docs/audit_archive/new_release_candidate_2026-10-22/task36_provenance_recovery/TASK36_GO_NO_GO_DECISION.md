# Task 36 — Go/No-Go Dataset Decision

## Overall decision

**NO-GO for the existing local dataset in the controlled new-release path.**

Eligibility is `BLOCKED_INSUFFICIENT_EVIDENCE`. The recovery attempt did not
find an authenticated acquisition chain, source-to-local mapping, or
rights-holder permission.

## Activity decisions

| Activity | Decision |
|---|---|
| Training and internal evaluation | `CONDITIONAL_PENDING_CONFIRMATION` |
| Distribution of trained model artifacts | `BLOCKED_INSUFFICIENT_EVIDENCE` |
| Public inference hosting, including commercial use | `BLOCKED_INSUFFICIENT_EVIDENCE` |
| Redistribution of original CSVs or derived dataset content | `BLOCKED_INSUFFICIENT_EVIDENCE` |

No activity is marked `SUPPORTED_BY_VERIFIED_EVIDENCE`. No activity is marked
`PROHIBITED_BY_DOCUMENTED_TERMS`; the available records are incomplete rather
than an explicit prohibition.

## Evidence supporting the no-go

- Current file sizes and SHA-256 values match local records only.
- The downloader names possible sources but does not record which source was
  used or preserve the source digest and transformation receipt.
- The Hugging Face record reports unknown license metadata and does not map its
  hosted artifacts to the local CSV bytes.
- The Kaggle record lists a license and filenames, but displayed counts differ
  from the local files and uploader authority over third-party content is not
  established.
- No acquisition log, license snapshot, rights-holder correspondence, or
  authenticated permission was found in the repository records.

## Required release decision

The project owner must either:

1. recover the records requested in `TASK36_UNSENT_PERMISSION_INQUIRY.md` and
   have them independently reviewed and bound into the secure preflight; or
2. authorize a separately licensed replacement dataset through a new,
   separately documented provenance and compatibility workflow.

The second option would be a new input and would not authenticate, reproduce,
or replace the historical dataset by implication. The candidate build must
remain disabled until the selected route satisfies the independent dataset,
   rights, grouping, environment, trust-root, and release-authorization gates.
