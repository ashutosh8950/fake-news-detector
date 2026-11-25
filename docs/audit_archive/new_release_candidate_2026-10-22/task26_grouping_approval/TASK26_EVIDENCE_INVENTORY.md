# Task 26 Evidence Inventory

## Scope and status

This inventory supports owner review of the grouping choice for a distinct future release. It is not an approval record and does not authenticate the historical production bundle. All decision fields remain pending in `GROUPING_POLICY_APPROVAL_TEMPLATE.json`.

HEAD before and after: `8c41ae005f4bee178a2b0104cb29049f00182081`. Existing working-tree modifications and untracked paths were preserved; only this new Task 26 directory was created.

## Directly verified in this audit

| Evidence | Path | Verification performed | Classification |
|---|---|---|---|
| Policy definitions and fingerprints | `duplicate_aware_manifest.py` | Read source constants and canonical configuration logic | Direct local evidence |
| All-key outer/inner manifests | `evaluation_results/duplicate_aware/final_v5/primary/` | Read metadata/summaries; calculated file SHA-256 read-only | Local consistency evidence |
| Body/combined outer/inner manifests | `evaluation_results/duplicate_aware/final_v5/body_combined_only/` | Read metadata/summaries; calculated file SHA-256 read-only | Local consistency evidence |
| Reservation records | Each policy `group_summary.json` | Parsed embedded reservation hash/count/result fields | Local algorithm-output evidence; no separate certificate file found |
| Source metadata | Each policy provenance object | Read recorded rows, sizes, schema fingerprints, and source hashes; dataset contents not read | Local consistency evidence only |
| Existing v3 validation | `evaluation_results/group_aware_model_evaluation/v3/manifest_validation.json` | Read JSON claims for coverage, crossings, and disjointness | Existing validation record, not rerun here |

## Policy evidence matrix

| Policy | Config fingerprint | Mixed labels | Reservation | Outer rows train/test | Existing validation |
|---|---|---:|---|---:|---|
| `all_keys_v1` | `c0bd2fb96caccd8b4ad75177ecf1625b11ad9107346775ada00fdd52cf911f9b` | 3 | 129 groups; hash `7af88dd07e099e81539fa962fc4a1578cfb6ed8ed3d1f549c088230faa74cc94` | 20,700 / 3,653 | v3 reports no crossings, exact source coverage, and outer-test disjointness |
| `body_combined_only_v1` | `824aeec9c7b2633446616ae297a43a7764b9a0de6c166e393f251322a3b64243` | 0 | 220 groups; hash `c8ae5a7cfd5d9dfbcc6192885ef1f77bb275156bc39054a868b340ea232ce52c` | 20,800 / 3,553 | v3 reports no crossings, exact source coverage, and outer-test disjointness |

## Hash register

These values were calculated during the audit for the named local files. They are not signatures and do not prove source authenticity.

| File | SHA-256 |
|---|---|
| `primary/split_manifest.csv` | `AFE2A950C8F7AD81AE50107BEF8BFBA5D463574B6A79728F503CD4A716288F6F` |
| `primary/inner_split_manifest.csv` | `BB617C0FC7CF1DF787B31BF7F89FC68CC7A58C12756737FAB42C46DFC0A865BE` |
| `primary/group_summary.json` | `002326842B762895F0B1B6CE5AE34091AF63D06781542C96F76F94C0C1024A93` |
| `primary/preflight_report.json` | `401280F3D3EB997A719E3EDA830A3C1364D60B64E2425D0735A8FAC7DBC4F909` |
| `body_combined_only/split_manifest.csv` | `50B548EAE6F904347650BCBE7C61B017166118C57A9AE59B56454B807F591728` |
| `body_combined_only/inner_split_manifest.csv` | `6DF90DE2967358722E00F319C923C0C7A74A03BCB9843CABE0978A3B94ED6407` |
| `body_combined_only/group_summary.json` | `480C90A2C9D8BFA43CEEF3999F6F64CA62ABA559B99BCFAA25615D5B4A07177D` |
| `body_combined_only/preflight_report.json` | `7F53D63EC4D65008D3245A7EA87ED9B1BA765E8B73781DFD79465E3834CB45B0` |

## Prior records inspected

- `evaluation_results/group_aware_model_evaluation/v2/evaluation_summary.md`: earlier evaluation record; explicitly documents a different preprocessing/environment context and non-comparable policy populations.
- `evaluation_results/group_aware_model_evaluation/v3/protocol.md` and `evaluation_summary.md`: frozen production-equivalent evaluation protocol and separate policy results; warns that test populations differ.
- `evaluation_results/group_aware_model_evaluation/v3/manifest_validation.json`, `manifest_configuration_fingerprints.json`, and `source_provenance.json`: validation, fingerprints, and local source provenance records.
- `evaluation_results/new_release_candidate_2026-10-22/NEW_RELEASE_CANDIDATE_REPORT.md`: Task 21 pre-build stop.
- `.../harness/TASK22_HARNESS_REPORT.md`, `TASK23_HARNESS_HARDENING_REPORT.md`, `TASK24_INDEPENDENT_VERIFICATION_REPORT.md`: isolated harness and synthetic hardening evidence.
- `.../environment_task25/TASK25_ENVIRONMENT_REPRODUCIBILITY_REPORT.md` and `TASK25_LOCK_GAP.md`: environment characterization and unresolved lock/offline-reconstruction gaps.

No standalone files named as Task 9, Task 10, or Task 11 reports were found. The v2/v3 records and the prior audit reports are the available repository evidence used here.

## Unresolved requirements

1. Dataset publisher, acquisition, licensing, and upstream authenticity remain unresolved.
2. The owner has not selected or approved either grouping policy for the new release.
3. Mixed-label acceptance for all-key and title-only duplicate treatment for body/combined require an explicit decision.
4. Candidate partition suitability must be revalidated against the exact approved source inputs before a build.
5. Complete environment locking, isolated real-data runner review, and release authentication remain separate gates.

## Audit boundaries

No dataset contents were processed, no model artifact was loaded, no training or evaluation was run, and no existing manifest, certificate, source data, report, or production file was modified. The evidence package contains observed local hashes and previously recorded metadata only; it does not add provenance.
