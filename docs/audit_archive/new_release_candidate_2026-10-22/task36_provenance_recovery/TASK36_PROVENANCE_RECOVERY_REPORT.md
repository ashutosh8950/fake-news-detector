# Task 36 — Provenance Recovery and Rights-Verification Report

## Decision summary

**Recovery result: no trustworthy historical provenance or rights authorization
was recovered. Overall dataset eligibility: `BLOCKED_INSUFFICIENT_EVIDENCE`.**

The current files can be identified locally and their bytes match the prior
local records, but the repository does not contain an acquisition event, exact
source revision, source artifact digest, transformation receipt, license
snapshot, or rights-holder permission. Public source records previously
inspected identify plausible datasets but do not authenticate the mapping to
the local files. The secure candidate preflight remains unchanged and blocked.

## Git and safety record

HEAD before and after: `8c41ae005f4bee178a2b0104cb29049f00182081` on `main`.
The pre-existing modified and untracked paths were preserved. No commit, push,
tag, reset, clean, deployment, training, calibration, evaluation, model
loading, dataset download, or configuration change occurred.

## Files and records inspected

Local source and records:

- `download_data.py`
- `evaluation_results/group_aware_model_evaluation/v3/source_provenance.json`
- `evaluation_results/group_aware_model_evaluation/v1/source_provenance.json`
- `evaluation_results/group_aware_model_evaluation/v2/source_provenance.json`
- `evaluation_results/group_aware_model_evaluation/v3/run_log.txt`
- `evaluation_results/group_aware_model_evaluation/v3/environment_versions.json`
- `evaluation_results/new_release_candidate_2026-10-22/task27_dataset_provenance/*`
- `evaluation_results/new_release_candidate_2026-10-22/task35_dataset_evidence/*`
- `PROJECT_MASTER_DOCUMENTATION.md`
- `PROJECT_DOCUMENTATION_INDEX.md`
- `PROJECT_DOCUMENTATION_COVERAGE.md`
- repository Git history for `download_data.py`, `data/Fake.csv`, and `data/True.csv`

Read-only file metadata and SHA-256 hashing were performed without parsing CSV
rows:

| File | Size | SHA-256 |
|---|---:|---|
| `data/Fake.csv` | 30,163,788 bytes | `672ab39a75ac75fef9ecbb1a84e2936e064b44a32197a4801d9d0fb63ca9d57e` |
| `data/True.csv` | 34,031,181 bytes | `c3105d9266fd2ad484aad43b13801930434ffcd68894cc975128e52433a0c6ad` |

The hashes match the existing v3 local provenance record. This is consistency
evidence only.

## Evidence recovered

### Acquisition and source mapping

`download_data.py` documents two possible routes:

1. Hugging Face `GonzaloA/fake_news`, using a `train.csv` URL and transforming
   its `label` column into `Fake.csv` and `True.csv`.
2. A Kaggle page for `clmentbisaillon/fake-and-real-news-dataset`, presented as
   a manual alternative.

The script can also write a small embedded sample dataset. No log records which
route was executed for the current files. The Git history contains commits for
the downloader, but no tracked history for the local CSV files or a recorded
acquisition event.

The local records contain schema, row counts, label rules, sizes, and hashes;
they contain no source revision, source digest, acquisition timestamp,
transformation receipt, license snapshot, or permission.

### Official public records already inspected

Access date: **2026-10-22**.

- [Hugging Face dataset page](https://huggingface.co/datasets/GonzaloA/fake_news)
  shows a roughly 24.4k-row train split and public dataset metadata.
- [Hugging Face commit `b690c7927f78544dc08a6a4817e50e7384182024`](https://huggingface.co/datasets/GonzaloA/fake_news/commit/b690c7927f78544dc08a6a4817e50e7384182024)
  records a 2022-12-09 Parquet conversion and hosted-object metadata, not the
  local CSV pair.
- [Hugging Face dataset README](https://huggingface.co/datasets/GonzaloA/fake_news/raw/main/README.md)
  reports an unknown license and names a curator/contact, but does not grant
  the intended project rights.
- [Kaggle dataset page](https://www.kaggle.com/datasets/clmentbisaillon/fake-and-real-news-dataset)
  lists `Fake.csv`/`True.csv`, displayed counts 23,502/21,417, and CC
  BY-NC-SA 4.0. Those counts differ from the local files, and no authenticated
  mapping or rights-holder authority record was found.

These records establish public page contents only. They do not establish that
the current files came from those pages or that the uploader controlled all
third-party article rights.

## Recovery result

No evidence was found for:

- original acquisition date, command, account, or process;
- exact upstream source file and revision used;
- a trusted source-file digest matching either local CSV;
- deterministic source-to-local transformation outputs and receipt;
- an archived license version covering the exact material;
- written permission from a rights holder;
- authority of the uploader over embedded news articles, metadata, or
  third-party content.

The recovery attempt therefore failed to establish historical provenance or
permission. Matching filenames, approximate row totals, local hashes, or
downloader URLs were not promoted to provenance evidence.

## Intended-use decision

| Activity | Decision | Basis |
|---|---|---|
| Training and internal evaluation | `CONDITIONAL_PENDING_CONFIRMATION` | Local files are available and identified, but origin and permission for the exact corpus/use are unresolved. |
| Trained-model artifact distribution | `BLOCKED_INSUFFICIENT_EVIDENCE` | No permission explicitly covers derived-model distribution. |
| Public inference hosting, including commercial use | `BLOCKED_INSUFFICIENT_EVIDENCE` | Hosting scope, commercial status, attribution, privacy, takedown, and derivative-use rights are unresolved. |
| Redistributing original CSVs or derived dataset content | `BLOCKED_INSUFFICIENT_EVIDENCE` | No authenticated source mapping or redistribution permission exists. |

No activity is classified as `PROHIBITED_BY_DOCUMENTED_TERMS`; the evidence is
insufficient rather than a documented prohibition. No activity is
`SUPPORTED_BY_VERIFIED_EVIDENCE`.

## Required next action

Send the unsent inquiry in `TASK36_UNSENT_PERMISSION_INQUIRY.md` through an
appropriate project-owner or rights-holder channel. Do not invent a recipient
or send it from this repository. Require authenticated source identity,
source-to-local mapping, rights-holder authority, and explicit scope for each
intended use. If this cannot be recovered, the owner should authorize a
separately licensed replacement dataset as a distinct new input; do not switch
datasets automatically or claim historical equivalence.
