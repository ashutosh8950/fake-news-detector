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
| E6 | polsci cleaned main, LinearSVC | 56.04% | 0.627431 | 480 rows |
| E6 | RealFakeNews cleaned article-length, inverted labels | 98.39% | 0.997838 | 17,159 rows |
| E6 | RealFakeNews short/headline-only, inverted labels | 59.08% | 0.226517 | 63,482 rows |
| E6 | formatted trusted IDs 1/6/7, LinearSVC | 86.81% | 0.953076 | 20,836 rows |
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

E6 was previously invalid: the old run used the wrong polsci mapping, did not detect RealFakeNews's 25,734 exact normalized-body overlaps with ISOT, did not perform the required near-duplicate check, blended unreliable formatted dataset IDs, and reported a network-blocked placeholder. The corrected local-file run normalizes labels from manual samples, removes exact and 5-word-shingle MinHash/Jaccard near duplicates at 0.8, filters English non-empty article-length rows, and reports reverse-label AUC only as a diagnostic. RealFakeNews is not a trustworthy benchmark despite its high corrected AUC: it is label-inverted/noisy and has substantial ISOT overlap. The exact counts and per-ID results are in `e6_external.json`.

### Corrected E6 details

| Dataset/subset | Before | Exact removed | Near removed | After main | LinearSVC accuracy | Fake recall | Real recall | ROC-AUC | Predicted Fake |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| polsci main | 480 | 0 | 0 | 480 | 56.04% | 87.50% | 24.58% | 0.627431 | 81.46% |
| RealFakeNews article-length | 108,032 | 25,734 | 31 | 17,159 | 98.39% | 98.10% | 98.69% | 0.997838 | 51.17% |
| RealFakeNews short/headline | 108,032 | 1,515 | 1 | 63,482 | 59.08% | 87.64% | 5.09% | 0.226517 | 90.15% |
| formatted trusted IDs 1/6/7 | 149,045 | 46,320 | 228 | 20,836 | 86.81% | 94.28% | 79.50% | 0.953076 | 57.01% |

RealFakeNews manual review estimated 5 noisy/apparently wrong labels in 30 samples after applying the inverted mapping. For `fake_news_formated`, IDs 0, 2, 4, 5, and 8 were excluded: IDs 0/4/5 had empty or unusable content, ID 2 showed label inversion in samples, and ID 8 showed unreliable mixed labels. Trusted IDs 1, 6, and 7 are reported separately in `e6_external.json`; ID 1 was highly consistent, while IDs 6 and 7 were weak/near-chance and should not be treated as strong benchmarks.

### E6 Tasks 1–3: ISOT sibling and similarity analysis

Pattern rates (% of rows containing the marker):

| Subset | `(Reuters)` | Reuters dateline | Apostrophe-stripped (`it s`, `can t`, `don t`) |
|---|---:|---:|---:|
| ISOT train | 52.40% | 48.37% | 35.92% |
| RealFakeNews article-length | 19.68% | 18.00% | 16.42% |
| fake_news_formated | 25.70% | 23.59% | 21.46% |
| polsci | 0.00% | 0.00% | 0.00% |

RealFakeNews raw-label/publisher cross-tab shows the inversion clearly: `(Reuters)` was present in 21,247 raw-FAKE rows and only 9 raw-REAL rows; absent in 22,144 raw-FAKE and 64,632 raw-REAL rows. Since the raw-FAKE samples were Reuters/fact-check reporting, the corrected mapping is raw FAKE → real and raw REAL → fake. This subset is not independent: 25,734 exact normalized-body matches with ISOT were removed, and its residual Reuters/apostrophe style remains strongly sibling-like.

| Subset | Clean rows used for similarity | Accuracy | AUC | Mean cosine to ISOT-train centroid | Nearest ISOT cosine >0.5 |
|---|---:|---:|---:|---:|---:|
| polsci | 480 | 56.04% | 0.6274 | 0.0924 | 3.54% |
| RealFakeNews article-length | 17,086 | 98.39% | 0.9978 | 0.1584 | 13.35% |
| RealFakeNews short/headline | 63,483 | NOT FOUND | NOT FOUND | 0.0335 | 0.86% |
| formatted ID 1 | 15,175 | 99.39% | 0.9998 | 0.1597 | 13.33% |
| formatted ID 2 | 37,631 | excluded | excluded | 0.1485 | 8.12% |
| formatted ID 5 | 2,600 | excluded | excluded | 0.0672 | 0.04% |
| formatted ID 6 | 1,806 | 51.44% | 0.6023 | 0.1206 | 0.83% |
| formatted ID 7 | 3,829 | 53.53% | 0.5973 | 0.1611 | 4.47% |
| formatted ID 8 | 1,423 | excluded | excluded | 0.1716 | 6.39% |

Nearest-neighbour percentages use a fixed random sample of 5,000 ISOT training rows for tractability; centroid similarity uses the full ISOT training partition and TF-IDF is fit on ISOT train only. Across valid rows, Pearson correlation between similarity and accuracy is 0.585; similarity and AUC is 0.571. This is association, not evidence that similarity causes accuracy.

The complete per-ID table, pattern CSV, similarity CSV, and plot are in `e6_similarity_analysis.json`, `e6_pattern_comparison.csv`, `e6_similarity_table.csv`, and `figures/e6_similarity_vs_accuracy.png`. IDs 0–8 are represented; IDs with no usable article-length rows have no score.

The 96.80% in-domain grouped-split accuracy measures performance on this dataset's source, time, topic, and writing-style mixture after duplicate groups are separated. It does not measure fact-checking ability, publisher-held-out generalization, time-held-out generalization, or performance on outside data. Higher ISOT similarity is associated with higher measured accuracy/AUC here, but the relationship is confounded by shared source, formatting, topics, and labels. RealFakeNews is invalid as an independent benchmark; formatted ID 1 is only a source-specific sibling stress test; IDs 6/7 are weak; and polsci is small. We still cannot claim robust real-world or out-of-domain accuracy.

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
