# Task 26 — Grouping Policy Review and Approval Package

## Executive result

**CONDITIONAL PASS for decision-package quality; NOT release-ready.** The repository contains two technically defined, deterministic duplicate-aware policies with read-only evidence of complete, group-disjoint manifests. The evidence does not constitute owner approval, dataset authenticity, licensing approval, dependency reproducibility, historical artifact provenance, or release authentication. No real-data training, model loading, evaluation, or manifest regeneration was performed.

The package therefore leaves every release-affecting decision **PENDING**. The next action is an owner decision on the grouping policy and exact partition artifacts, followed by separate resolution of the remaining provenance, environment, runner, and authentication gates.

## Git and scope record

HEAD before and after the audit: `8c41ae005f4bee178a2b0104cb29049f00182081` on `main`. The pre-audit working tree already contained the modified tracked files `README.md`, `app.py`, `download_models.py`, `frontend/style.css`, `predictor.py`, and `routers/api.py`, plus the previously untracked documentation, source, test, and evaluation paths recorded by `git status --short`. The post-audit status preserves all of those entries and adds no separately tracked change; the only files created by this task are the three files in `task26_grouping_approval/`. No prior report, manifest, certificate, source-data file, or model artifact was modified.

## Evidence classification

- **Directly verified in this audit:** source definitions and fingerprints in `duplicate_aware_manifest.py`; existing JSON/CSV files exist; their listed SHA-256 values were calculated read-only; manifest summaries and validation records were parsed without reading the training data files.
- **Previously reported / existing evaluation evidence:** protocol and metric claims in `group_aware_model_evaluation/v2` and `v3`, and the Task 21–25 reports. These are treated as repository records, not independent authentication or owner approval.
- **Interpretation/recommendation:** the trade-off discussion and proposed approval gates below.
- **Still required from the owner:** policy selection, source-hash acceptance, exact-manifest acceptance, mixed-label/leakage limitation acceptance, and authorization to proceed after all other gates pass.

## Policy definitions

Both policies use the same normalization, graph, schema, and split framework:

| Field | Value |
|---|---|
| Normalization | `unicode_alphanumeric_v2` — NFKC, casefold, non-alphanumeric separators, collapsed ASCII spaces, trim |
| Grouping | `transitive_key_components_v1` |
| Split | `deterministic_group_split_v2`, metadata random state 42 |
| Manifest schema | `duplicate_aware_manifest_v2` |
| Outer target | 85% train / 15% test |
| Inner target | 64% proper-fit / 16% method-selection / 20% final-calibration |

`all_keys_v1` groups connected rows using title, body, and combined normalized keys. `body_combined_only_v1` uses body and combined keys, intentionally excluding title-only matches. The implementation’s reservation certificate is embedded in `group_summary.json`; no separate certificate file was found in the final_v5 directories.

## Input and policy evidence

The local source records identify two input files. These hashes are **local integrity/consistency records only**, not independently authenticated dataset provenance:

| Input | Rows | Size | SHA-256 | Schema fingerprint |
|---|---:|---:|---|---|
| `data/Fake.csv` | 11,107 | 30,163,788 | `672ab39a75ac75fef9ecbb1a84e2936e064b44a32197a4801d9d0fb63ca9d57e` | `17c163df559764e031edaf2188a3b24e1bc8d69cfeaaae02cc0bd5bb157e7a5c` |
| `data/True.csv` | 13,246 | 34,031,181 | `c3105d9266fd2ad484aad43b13801930434ffcd68894cc975128e52433a0c6ad` | same |

| Policy | Configuration fingerprint | Manifest | Manifest SHA-256 | Group summary SHA-256 |
|---|---|---|---|---|
| `all_keys_v1` | `c0bd2fb96caccd8b4ad75177ecf1625b11ad9107346775ada00fdd52cf911f9b` | `evaluation_results/duplicate_aware/final_v5/primary/split_manifest.csv` | `AFE2A950C8F7AD81AE50107BEF8BFBA5D463574B6A79728F503CD4A716288F6F` | `002326842B762895F0B1B6CE5AE34091AF63D06781542C96F76F94C0C1024A93` |
| `body_combined_only_v1` | `824aeec9c7b2633446616ae297a43a7764b9a0de6c166e393f251322a3b64243` | `evaluation_results/duplicate_aware/final_v5/body_combined_only/split_manifest.csv` | `50B548EAE6F904347650BCBE7C61B017166118C57A9AE59B56454B807F591728` | `480C90A2C9D8BFA43CEEF3999F6F64CA62ABA559B99BCFAA25615D5B4A07177D` |

Inner-manifest hashes are `BB617C0FC7CF1DF787B31BF7F89FC68CC7A58C12756737FAB42C46DFC0A865BE` (all-key) and `6DF90DE2967358722E00F319C923C0C7A74A03BCB9843CABE0978A3B94ED6407` (body/combined). The corresponding `preflight_report.json` hashes are `401280F3D3EB997A719E3EDA830A3C1364D60B64E2425D0735A8FAC7DBC4F909` and `7F53D63EC4D65008D3245A7EA87ED9B1BA765E8B73781DFD79465E3834CB45B0`.

Reservation hashes embedded in the group summaries are `7af88dd07e099e81539fa962fc4a1578cfb6ed8ed3d1f549c088230faa74cc94` (129 reserved groups) and `c8ae5a7cfd5d9dfbcc6192885ef1f77bb275156bc39054a868b340ea232ce52c` (220 reserved groups). The final-v5 records show zero accepted changes and `optimization_limit_reached=false`; this is evidence of the recorded algorithm outcome, not proof of global optimality.

## Partition and validation comparison

| Policy | Inner partitions (rows / groups) | Class counts (0 Fake / 1 Real) | Mixed-label groups | Group overlap evidence |
|---|---|---|---:|---|
| `all_keys_v1` | proper-fit 13,248 / 13,083; selection 3,282 / 3,267; calibration 4,170 / 4,155 | 6,042/7,206; 1,481/1,801; 1,918/2,252 | 3 | Existing v3 validation reports zero inner/outer crossings, exact source coverage, and outer-test disjointness |
| `body_combined_only_v1` | proper-fit 13,412 / 13,412; selection 3,168 / 3,168; calibration 4,220 / 4,220 | 6,124/7,288; 1,439/1,729; 1,928/2,292 | 0 | Existing v3 validation reports zero inner/outer crossings, exact source coverage, and outer-test disjointness |

Existing v3 validation records report outer partitions of 20,700/3,653 rows for all-key and 20,800/3,553 for body/combined, with 24,353 unique row IDs and no duplicate row IDs. The same records report 24,053 groups for all-key and 24,349 for body/combined. These are read-only records from the repository; they were not regenerated here.

The all-key policy is stricter against duplicates represented by title-only links, but its recorded graph contains three mixed-label groups. The body/combined policy has no recorded mixed-label groups and slightly more groups, but it deliberately does not connect title-only duplicates. Neither policy is automatically preferable: the choice depends on the owner-approved definition of leakage and acceptable mixed-label handling. The different outer-test populations mean reported scores cannot be used as a controlled head-to-head comparison.

## Existing evaluation context

The v3 protocol states that preprocessing, vectorizers, model selection, calibration, and outer-test access were separated, with labels `0 = Fake`, `1 = Real`; it records the two policies as separate protocols. Its summary reports Decision Tree selected for both policies, but explicitly warns that their test populations differ. Earlier v2 evidence used a different preprocessing/environment context and is not a substitute for a new-release approval. No standalone Task 9, Task 10, or Task 11 report file was found by the repository file search; relevant v2/v3 records and the prior audit reports were inspected instead.

The Task 21–25 reports document that real-data release work remains blocked by unresolved dataset origin/licensing, complete dependency locking, owner-approved new-release policy/partitions, isolated runner review, and release authentication. The grouping package does not close those gates.

## Owner decision record — all pending

1. **Selected grouping policy:** `PENDING` — choose `all_keys_v1`, `body_combined_only_v1`, or request a separately reviewed policy.
2. **Exact source data hashes:** `PENDING` — approve the two exact local source records above for this candidate build, subject to provenance/licensing review.
3. **Configuration fingerprint:** `PENDING` — approve the selected policy’s exact fingerprint and implementation revision.
4. **Partition manifest and hash:** `PENDING` — approve the exact outer and inner manifest files, their hashes, and embedded reservation evidence.
5. **Known limitations:** `PENDING` — explicitly accept or reject mixed-label behavior, normalized-key limitations, and the non-global-optimality limitation.
6. **Isolated build authorization:** `PENDING` — authorize only after dataset licensing/provenance, environment, runner, partition validation, and all other pre-build gates pass.

Approval of this package would not establish dataset licensing, historical model authenticity, dependency reproducibility, or release signing. It would also not authorize production deployment.

## Release-gate recommendation

Before an isolated real-data build, require the selected policy and exact hashes to be recorded in an owner-approved decision record, independently revalidate the source files and manifest, verify the owner-approved grouping policy and partition assignments, and pass the existing refusal-default harness gates. Keep the historical bundle blocked. A future candidate remains a new release even if it uses these existing policies.

## Files inspected

- `duplicate_aware_manifest.py`
- `evaluation_results/duplicate_aware/final_v5/primary/{split_manifest.csv,inner_split_manifest.csv,group_summary.json,preflight_report.json}`
- `evaluation_results/duplicate_aware/final_v5/body_combined_only/{split_manifest.csv,inner_split_manifest.csv,group_summary.json,preflight_report.json}`
- `evaluation_results/group_aware_model_evaluation/v2/evaluation_summary.md`
- `evaluation_results/group_aware_model_evaluation/v3/{protocol.md,evaluation_summary.md,manifest_validation.json,manifest_configuration_fingerprints.json,source_provenance.json}`
- `evaluation_results/new_release_candidate_2026-10-22/{NEW_RELEASE_CANDIDATE_REPORT.md,harness/TASK22_HARNESS_REPORT.md,harness/TASK23_HARNESS_HARDENING_REPORT.md,harness/TASK24_INDEPENDENT_VERIFICATION_REPORT.md,environment_task25/TASK25_ENVIRONMENT_REPRODUCIBILITY_REPORT.md,environment_task25/TASK25_LOCK_GAP.md}`

The exact paths, classifications, and hash status are indexed in `TASK26_EVIDENCE_INVENTORY.md`. This audit did not read dataset contents, model artifacts, or alter any existing file.
