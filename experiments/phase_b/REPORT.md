# Phase B: Shortcut-Learning Audit

Branch: `phase-b-audit`  
Split: existing `final_v5/primary` duplicate-aware grouped split  
Seed: `42`  
TF-IDF: fit on the training partition only.  
Production models, artifacts, and API: not modified.

## Preprocessing decision

The light preprocessor applies the production cleaning rules and stopword filtering but does not lemmatize with spaCy. Compared with the prior spaCy E1 result, light-preprocessor accuracy changed by +0.33 percentage points for LR (95.89% to 96.22%), +0.22 points for LinearSVC (96.58% to 96.80%), and +0.30 points for NB (93.48% to 93.79%). All are within the required one-point tolerance, so E3–E5 use the light preprocessor. E2 uses the cached spaCy-preprocessed corpus. The cache is outside the repository, hash-keyed to the input data and preprocessing code, resumable, and built with `nlp.pipe(batch_size=500, n_process=max(1, cpu_count()-1))`.

## Results

| Experiment | Model/condition | Accuracy | ROC-AUC / artifact share | Status |
|---|---|---:|---:|---|
| E1 | LR, light preprocessing | 96.22% | 0.992343 | complete |
| E1 | LinearSVC, light preprocessing | 96.80% | 0.993759 | complete |
| E1 | NB, light preprocessing | 93.79% | 0.980337 | complete |
| E2 | LR fake top-50 artifact share | — | 6.0% | complete |
| E2 | LR real top-50 artifact share | — | 30.0% | complete |
| E3 | LinearSVC original→original | 96.80% | 0.993759 | complete |
| E3 | LinearSVC stripped→stripped | 96.11% | 0.991427 | complete |
| E3 | LinearSVC original→stripped | 96.28% | 0.990309 | complete |
| E3 | LinearSVC stripped→original | 96.14% | 0.991588 | complete |
| E4 | title only | 90.72% | 0.968688 | complete |
| E4 | body first 300 characters | 95.43% | 0.986349 | complete |
| E4 | non-lexical style only | 76.18% | 0.845836 | complete |
| E4 | character TF-IDF, first 50 characters | 96.36% | 0.983080 | complete |
| E5 | original model, title only | 85.14% | — | complete |
| E5 | stripped model, title only | 86.15% | — | complete |
| E5 | original model, first sentence | 94.94% | — | complete |
| E5 | stripped model, first sentence | 90.86% | — | complete |
| E5 | original model, first two sentences | 95.46% | — | complete |
| E5 | stripped model, first two sentences | 93.62% | — | complete |
| E6 | external datasets | NOT FOUND | NOT FOUND | network blocked |
| E3b | v1 stripped→stripped, LinearSVC | 96.11% | 0.991427 | complete |
| E3b | v2 stripped→stripped, LinearSVC | 95.92% | 0.990683 | complete |
| E3b | v1 char TF-IDF first 50 | 87.74% | 0.947344 | complete |
| E3b | v2 char TF-IDF first 50 | 87.87% | 0.946419 | complete |

The held-out test set contains 3,653 rows: 1,666 fake and 1,987 real. Full per-class metrics, confusion matrices, feature lists, before/after examples, and short-input fake percentages are in the experiment JSON files.

## E3b residual shortcut audit

The v1 stripped LR top-50 features were classified as 82% content words, 6% outlet/format artifacts, and 12% time/topic artifacts for fake-associated features; real-associated features were 54% content, 0% outlet/format, and 46% time/topic. Residual artifacts included `video`, `watch`, `breitbart`, politician names, weekday/month tokens, `government`, `parliament`, and election phrases. The 30-example samples are stored in `e3b_residual_shortcuts.json` and are printed by the script.

The v1 and v2 first-50-character probes were 87.74% and 87.87%, respectively. v2 did not improve this residual probe. The v2 stripped→stripped LinearSVC result was 95.92%, 0.19 points below v1 and 0.88 points below the original 96.80% baseline. Topic/time counts showed strong class-specific concentration: on the held-out set, `trump` occurred 6,366 times in fake examples versus 4,217 in real examples, while `donald`, `obama`, `clinton`, `hillary`, `america`, and `muslim` were prominent in fake examples; `north`, `korea`, `china`, `iran`, and `parliament` were prominent in real examples. These are correlations, not causal evidence.

## E7 verdict

The controlled marker-stripping result gives a directly measured shortcut effect of approximately 0.68 percentage points for the best model: LinearSVC falls from 96.80% to 96.11% when both training and test text are stripped. This is not a complete “fraction of accuracy” decomposition; the high 96.36% first-50-character character model and 76.18% style-only model show additional formatting/style signal that marker stripping does not remove. Therefore, at least a measurable ~0.7 points of headline accuracy is associated with removable source/format markers, while the total shortcut contribution is NOT IDENTIFIABLE from these probes alone.

E6 external generalization was not evaluated because the environment blocked the Hugging Face datasets-server connection with Windows `WinError 10013`. No external accuracy is claimed. The exact manual Parquet paths are recorded in `e6_external.json`.

The 96.80% in-domain grouped-split accuracy measures performance on this dataset's source, time, topic, and writing-style mixture after duplicate groups are separated. It does not measure fact-checking ability, publisher-held-out generalization, time-held-out generalization, or performance on outside data. Until E6 is run on the downloaded external files, the model's real-world accuracy is NOT FOUND.

### Phase C recommendation

Add genuinely independent publishers, dates, topics, and geographies; include articles with source markers normalized or removed; and use publisher/time/topic-grouped splits with a fully held-out out-of-domain test set. Report performance separately on in-domain grouped data, source-held-out data, time-held-out data, and external datasets. The 50-character probe and style-only result should be treated as release-blocking evidence until these evaluations improve.

## Reproduction commands

Run from the repository root with the project environment active:

```powershell
python -m pip install datasets pyarrow pandas
& .venv\Scripts\python.exe -B experiments\phase_b\download_external.py
& .venv\Scripts\python.exe -B experiments\phase_b\prep_cache.py
& .venv\Scripts\python.exe -B experiments\phase_b\run_e1_baseline.py
& .venv\Scripts\python.exe -B experiments\phase_b\run_e2_top_features.py
& .venv\Scripts\python.exe -B experiments\phase_b\run_e4_probes.py
& .venv\Scripts\python.exe -B experiments\phase_b\run_e3_marker_stripping.py
& .venv\Scripts\python.exe -B experiments\phase_b\run_e5_short_input.py
& .venv\Scripts\python.exe -B experiments\phase_b\run_e6_external.py
& .venv\Scripts\python.exe -B experiments\phase_b\run_e3b_residual_shortcuts.py
```
