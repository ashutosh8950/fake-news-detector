# Task 35 — Dataset Provenance, Licensing, and Acquisition-Chain Evidence Audit

## Executive result

**CONDITIONAL PASS for the evidence audit; dataset eligibility remains `BLOCKED_INSUFFICIENT_EVIDENCE` for a controlled release.**

The current local files have reproducible local identity records and their
current byte hashes match those records. The repository documents two possible
upstream routes, Hugging Face and Kaggle, but records no historical acquisition
event, source artifact digest, authenticated source revision, transformation
receipt, or rights-holder authorization. Public source pages provide useful
description and licensing metadata, but do not prove that these exact local
bytes came from either source or that the uploader could grant all rights in
the embedded news content.

No training, evaluation, model loading, dataset download, artifact creation, or
candidate-gate modification occurred.

## Git and scope record

HEAD before and after: `8c41ae005f4bee178a2b0104cb29049f00182081` on `main`.

The pre-existing modified paths (`README.md`, `app.py`, `download_models.py`,
`frontend/style.css`, `phase2_calibration.py`, `predictor.py`, `routers/api.py`,
and `train.py`) and previously untracked files were preserved. Only the three
new files in `task35_dataset_evidence/` were created by this task.

## Local dataset identity

Read-only file metadata and byte hashing were performed on 2026-10-22. No CSV
rows were parsed.

| File | Size | Current SHA-256 | Prior-record match |
|---|---:|---|---|
| `data/Fake.csv` | 30,163,788 bytes | `672ab39a75ac75fef9ecbb1a84e2936e064b44a32197a4801d9d0fb63ca9d57e` | Yes |
| `data/True.csv` | 34,031,181 bytes | `c3105d9266fd2ad484aad43b13801930434ffcd68894cc975128e52433a0c6ad` | Yes |

The carried-forward schema is `title,text,subject,date`; the carried-forward
row counts are 11,107 and 13,246. These values come from
`evaluation_results/group_aware_model_evaluation/v3/source_provenance.json`
and earlier audits. Matching a local record establishes consistency with that
record only, not upstream authenticity.

The observed filesystem modification times were 2026-07-08, but they are not
treated as acquisition timestamps or provenance evidence.

## Local acquisition-chain evidence

`download_data.py` names:

- Hugging Face `https://huggingface.co/datasets/GonzaloA/fake_news/resolve/main/train.csv`
  as the primary download URL.
- Kaggle `https://www.kaggle.com/datasets/clmentbisaillon/fake-and-real-news-dataset`
  as a manual alternative in its user-facing instructions.

The script can transform a labeled table into `Fake.csv` and `True.csv`,
assigning labels from `label`, and can generate synthetic `subject` and `date`
fields. It can also create a small embedded demo dataset. The script therefore
documents possible behavior, not the historical path that created the current
files. There is no recorded acquisition date, source revision used, source
artifact hash, download log, account/process identity, or transformation output
receipt tied to the current files. Git history contains commits for the script,
but no tracked history for the local CSV files themselves.

## Public primary-source records inspected

Access date for all web research: **2026-10-22**.

### Hugging Face

- [Dataset page](https://huggingface.co/datasets/GonzaloA/fake_news): identifies
  the `GonzaloA/fake_news` dataset, a train split of approximately 24.4k rows,
  title/text/label fields, and current repository metadata showing an unknown
  license.
- [Historical commit `b690c7927f78544dc08a6a4817e50e7384182024`](https://huggingface.co/datasets/GonzaloA/fake_news/commit/b690c7927f78544dc08a6a4817e50e7384182024): dated 2022-12-09 and records conversion to Parquet; displayed Git-LFS OIDs and sizes exist for the hosted artifacts. It does not provide a digest for the local `Fake.csv`/`True.csv` pair or a source-to-local transformation receipt.
- [Raw dataset README](https://huggingface.co/datasets/GonzaloA/fake_news/raw/main/README.md): reports `license: unknown` in the dataset-card metadata. It names a curator/contact, but does not grant the project rights for training, derived-model distribution, public hosting, or redistribution of third-party article text.

The hosted row count is a consistency clue only. It does not establish byte
identity because the local files may have been filtered, reordered, relabeled,
transformed, or obtained through another route.

### Kaggle

- [Dataset page](https://www.kaggle.com/datasets/clmentbisaillon/fake-and-real-news-dataset): public metadata identifies `Fake.csv` and `True.csv`, describes the four columns, displays 23,502 fake and 21,417 true articles, and reports `CC BY-NC-SA 4.0`.

The displayed counts differ from the local files (11,107 and 13,246), and no
authenticated digest or acquisition mapping connects that page to the local
bytes. A platform listing and uploader identity do not by themselves establish
authority over every underlying article or permission for model distribution,
public hosting, or redistribution. The displayed CC BY-NC-SA metadata is
therefore recorded as authoritative hosting metadata, not as legal clearance
for this project’s intended uses.

## Source-to-local identity assessment

| Claim | Evidence state | Reason |
|---|---|---|
| Current local bytes match the prior local record | `CONSISTENCY_EVIDENCE_ONLY` | Recomputed SHA-256 values match `source_provenance.json`. |
| Local files came from the Hugging Face commit | `UNAVAILABLE` | No acquisition receipt, source-file digest mapping, or reproducible transformation record. |
| Local files came from the Kaggle dataset page | `UNAVAILABLE` | File names are suggestive, but counts differ and no authenticated byte mapping exists. |
| Local files were transformed by the current downloader | `UNAVAILABLE` | Script intent is recorded; execution history and source input are not. |
| The uploader could license all embedded article content | `UNAVAILABLE` | No rights-holder chain or permission record exists. |

## Intended-use classification

| Intended activity | Status | Evidence and unresolved issue |
|---|---|---|
| Model training/evaluation | `CONDITIONAL_PENDING_CONFIRMATION` | Local identity is recorded, but dataset origin and permission for this corpus/use are not authenticated. |
| Distribution of trained model artifacts | `BLOCKED_INSUFFICIENT_EVIDENCE` | No permission record covers derived-model or artifact distribution for the exact corpus. |
| Public inference hosting | `BLOCKED_INSUFFICIENT_EVIDENCE` | Hosting scope, commercial status, attribution/notice, privacy, takedown, and derivative-use permissions are unresolved. |
| Redistribution/publication of dataset contents | `BLOCKED_INSUFFICIENT_EVIDENCE` | No authenticated source mapping or authorization for redistribution exists. |

These are release-readiness classifications, not definitive legal opinions.
The underlying news articles may carry rights or restrictions that a dataset
uploader cannot waive.

## What would unblock each issue

1. The project owner or release authority must provide an acquisition record
   naming the exact source, version/commit, URL, acquisition date, process, and
   transformation steps.
2. An independently authenticated source artifact or archival copy and its
   SHA-256 must be supplied, together with a deterministic mapping to the exact
   local hashes listed above. The record must explain filtering, ordering,
   labels, and generated fields.
3. An original publisher, rights holder, or other demonstrably authorized party
   must provide the applicable version-specific license or written permission.
   It must explicitly cover training/evaluation, derived-model artifact
   distribution, public hosting, and—if planned—source-data redistribution.
4. The owner/legal reviewer must address third-party article rights, privacy,
   attribution, notices, takedown, non-commercial restrictions, and any
   derivative-work conditions.
5. The evidence must be bound into the candidate preflight as trusted source
   digests, source revision, intended-use scope, and an independently
   authenticated approval. An editable Boolean or unsigned local JSON record is
   insufficient.
6. Grouping/partition approval, dependency evidence, and release signing remain
   separate gates even after dataset permission is resolved.

## Final conclusion

The exact local datasets remain **blocked for a controlled new release**. The
minimum legitimate next action is to recover the acquisition and rights records
from the project owner or an authorized rights holder. If those records cannot
be recovered, the owner must authorize a different, clearly licensed dataset
and treat it as a new input with new provenance; that would not authenticate the
current historical files.

## Commands and records inspected

Read-only local commands included:

- `git rev-parse HEAD`
- `git status --short`
- `Get-Item data/Fake.csv,data/True.csv`
- `Get-FileHash -Algorithm SHA256 -LiteralPath data/Fake.csv` and the equivalent command for `data/True.csv`
- `Get-Content download_data.py`
- `Get-Content evaluation_results/group_aware_model_evaluation/v3/source_provenance.json`
- `git log --all --oneline -- download_data.py data/Fake.csv data/True.csv`

Public read-only sources were inspected at the URLs listed above on
2026-10-22. No release binaries, source dataset downloads, or package
artifacts were retrieved.
