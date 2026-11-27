# Task 27 — Dataset Provenance, Licensing, and New-Release Eligibility

## Executive result

**CONDITIONAL PASS for the evidence audit; new-release dataset eligibility remains `BLOCKED_INSUFFICIENT_EVIDENCE`.** The exact local files are unchanged and match the previously recorded local hashes, sizes, schemas, and row counts. Public records identify plausible upstream sources, but they do not authenticate the mapping from either source to these exact local bytes or establish that the relevant rights holder authorized training, artifact distribution, public hosting, or dataset redistribution.

No training, evaluation, model loading, dataset-content processing, download, or file modification occurred. This report does not authorize a build or release.

## Exact local dataset identity

The following values were verified read-only with file metadata and SHA-256. Row counts and schema are carried forward from the existing v3 provenance record; the CSV contents were not parsed in this task.

| Relative path | Size | SHA-256 | Recorded rows | Recorded schema | Match to prior record |
|---|---:|---|---:|---|---|
| `data/Fake.csv` | 30,163,788 bytes | `672ab39a75ac75fef9ecbb1a84e2936e064b44a32197a4801d9d0fb63ca9d57e` | 11,107 | `title,text,subject,date` | Yes |
| `data/True.csv` | 34,031,181 bytes | `c3105d9266fd2ad484aad43b13801930434ffcd68894cc975128e52433a0c6ad` | 13,246 | `title,text,subject,date` | Yes |

The exact comparison record is `evaluation_results/group_aware_model_evaluation/v3/source_provenance.json`. Matching a local record proves consistency with that record, not upstream authenticity.

## Provenance chain

### Direct local evidence

`download_data.py` names Hugging Face `GonzaloA/fake_news` `train.csv` as its primary URL and a Kaggle `clmentbisaillon/fake-and-real-news-dataset` page as a fallback instruction. The script transforms a downloaded labeled table into `Fake.csv` and `True.csv`, assigns synthetic subject/date values, and can also create a small embedded demo dataset. Therefore, the script documents possible acquisition paths, not the historical acquisition path of the current files.

The local provenance record maps every row from `Fake.csv` to label 0 and every row from `True.csv` to label 1. It does not record acquisition date, source revision, source-file digest, transformation output digest, license decision, or a chain of custody.

### Public source evidence

- The [Hugging Face dataset page](https://huggingface.co/datasets/GonzaloA/fake_news) identifies a public `GonzaloA/fake_news` dataset with a `train` split of approximately 24.4k rows and metadata showing `license: unknown`.
- The [Hugging Face README](https://huggingface.co/datasets/GonzaloA/fake_news/blob/main/README.md?code=true) identifies a dataset curator/contact and describes the dataset, but does not provide an authenticated mapping to the local CSVs or a permission statement for this project’s intended uses.
- The [Hugging Face historical commit](https://huggingface.co/datasets/GonzaloA/fake_news/commit/b690c7927f78544dc08a6a4817e50e7384182024) records a 24,353-row train split and no download checksums in the displayed metadata. The equal total row count is a consistency clue only; it does not prove byte identity, because local files may have been transformed, reordered, filtered, or relabeled.
- The [Kaggle dataset page](https://www.kaggle.com/datasets/clmentbisaillon/fake-and-real-news-dataset) lists `Fake.csv` and `True.csv`, describes four data columns, and labels the dataset `CC BY-NC-SA 4.0`. Its displayed counts (23,502 fake and 21,417 true) differ from the local files, and the page does not provide a signed digest or an authenticated local-file mapping. The uploader’s platform listing alone does not prove authority over every underlying article or grant this project’s intended rights.

These are authoritative public records about the hosted pages, not independently authenticated evidence about the local files. The previous public-source audit also recorded that exact project release pages and signatures were unavailable to its retrieval service; that limitation remains relevant to artifact provenance but is not treated as evidence of absence.

## Intended-use assessment

| Intended use | Status | Evidence basis and gap |
|---|---|---|
| Local experimentation and training | `CONDITIONAL_PENDING_CONFIRMATION` | The files are locally available and structurally recorded. Permission for this specific corpus and use is not established; owner/legal review is required. |
| Saving and distributing newly trained model artifacts | `BLOCKED_INSUFFICIENT_EVIDENCE` | No rights record establishes that model or derived-artifact distribution is permitted for the exact source material. |
| Public web inference hosting | `BLOCKED_INSUFFICIENT_EVIDENCE` | Public deployment adds commercial/public-use, notice, privacy, and derivative-use questions not resolved by a dataset page or attribution alone. |
| Redistributing the source dataset | `BLOCKED_INSUFFICIENT_EVIDENCE` | No authenticated source mapping or permission from a party authorized to grant redistribution rights was found. |

These are risk classifications for release readiness, not definitive legal opinions. A lawyer or authorized rights holder may resolve them with evidence that is absent here.

## Evidence classification

| Evidence item | Classification | What it supports | What remains unproven |
|---|---|---|---|
| Current local file hashes/sizes | `CONSISTENCY_EVIDENCE_ONLY` | Current bytes match prior local records | Authentic upstream origin or rights |
| v3 source provenance JSON | `AUTHORITATIVE LOCAL RECORD` | Recorded schema, rows, labels, and hashes | Independent acquisition/authentication |
| `download_data.py` URLs and transformations | `REPORTED HISTORICAL CLAIM / CODE INTENT` | Possible sources and transformation behavior | Actual historical execution and source version |
| Hugging Face dataset page/history | `AUTHORITATIVE BUT NOT CRYPTOGRAPHICALLY AUTHENTICATED` | Public dataset identity, row-count clue, unknown license metadata | Exact local-byte mapping and permission |
| Kaggle dataset page | `AUTHORITATIVE BUT NOT CRYPTOGRAPHICALLY AUTHENTICATED` | Public file names and displayed CC BY-NC-SA 4.0 listing | Local-byte mapping, uploader authority, rights to all content |
| Local Git history | `CONSISTENCY EVIDENCE ONLY` | Project code and references | Dataset acquisition event or license grant |
| Acquisition receipt, source digest, rights-holder permission | `UNAVAILABLE` | Would establish provenance/permission if independently authenticated | Must be supplied or recovered |

## Minimum evidence to unblock

The owner or release authority must supply or obtain all of the following, with independently verifiable records:

1. An acquisition record naming the source, exact version/commit, URL, date, account/process, and transformation steps.
2. A cryptographic digest of the source artifact and a reproducible, documented mapping from that source to the exact local `Fake.csv` and `True.csv` bytes, including filtering, ordering, relabeling, and generated fields.
3. The applicable version-specific license or written permission from a party authorized to grant it, covering at minimum local training, derived-model/artifact distribution, public web hosting, and—if planned—source-data redistribution.
4. A determination of whether the underlying news articles carry third-party restrictions that the dataset uploader could not waive.
5. An owner/legal decision identifying the intended release scope and accepting any restrictions, attribution, notice, takedown, or non-commercial conditions.
6. Separate approval of the grouping policy and exact partition manifests; dataset permission does not approve those technical controls.

Until items 1–5 are evidenced, the candidate must not train on these files for a release intended for distribution or public hosting. A replacement dataset with a clear license would be a different input and must receive its own provenance record.

## Git and safety record

HEAD before and after: `8c41ae005f4bee178a2b0104cb29049f00182081` on `main`. The pre-existing modified and untracked paths were preserved. The only new files created by this task are the three files under `evaluation_results/new_release_candidate_2026-10-22/task27_dataset_provenance/`.

No dataset contents were processed for model development; no datasets, models, packages, or external resources were downloaded; no artifacts, production files, manifests, or prior reports were modified. Public web pages were inspected only as lightweight metadata/documentation sources.

## Sources and limitations

Local sources inspected: `download_data.py`, `evaluation_results/group_aware_model_evaluation/v3/source_provenance.json`, `evaluation_results/model_reproducibility_release_plan_2026-10-21/MODEL_REPRODUCIBILITY_AND_RELEASE_PLAN.md`, `evaluation_results/historical_release_recovery_2026-10-21/HISTORICAL_RELEASE_RECOVERY_AUDIT.md`, and `evaluation_results/new_release_candidate_2026-10-22/NEW_RELEASE_CANDIDATE_REPORT.md`.

Public sources inspected on 2026-10-22 are linked above. Public pages can establish what a host currently displays; they do not by themselves establish uploader authority, historical file identity, or a license for all underlying content. No private records, credentials, or secrets were requested or accessed.
