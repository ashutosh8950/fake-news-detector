# Phase B: Shortcut-Learning Audit

Branch: `phase-b-audit`  
Split: existing `final_v5/primary` duplicate-aware grouped split  
Seed: `42`  
Production models, artifacts, and API: not modified.

## Execution status

Only E1 completed before the audit run was interrupted. E2–E6 are intentionally marked `NOT FOUND`; no results are inferred from unfinished runs. The temporary spaCy preprocessing cache was outside the repository and was not retained as an experiment output.

## Key results

| Experiment | Model/condition | Accuracy | ROC-AUC | Status |
|---|---|---:|---:|---|
| E1 | Logistic Regression | 95.8938% | 0.989162 | complete |
| E1 | LinearSVC | 96.5782% | 0.993226 | complete |
| E1 | MultinomialNB | 93.4848% | 0.977949 | complete |
| E2 | LR top-50 artifact share | NOT FOUND | NOT FOUND | not completed |
| E3 | marker stripping | NOT FOUND | NOT FOUND | not completed |
| E4 | signal-source probes | NOT FOUND | NOT FOUND | not completed |
| E5 | short-input robustness | NOT FOUND | NOT FOUND | not completed |
| E6 | external datasets | NOT FOUND | NOT FOUND | not completed |

E1 used TF-IDF fit on the training partition only, with the existing production preprocessing and grouped split. The held-out test set contained 3,653 rows: 1,666 fake and 1,987 real.

### E1 detailed metrics

| Model | Fake precision | Fake recall | Fake F1 | Real precision | Real recall | Real F1 | Confusion matrix |
|---|---:|---:|---:|---:|---:|---:|---|
| LR | 0.9438 | 0.9676 | 0.9555 | 0.9722 | 0.9517 | 0.9619 | `[[1612,54],[96,1891]]` |
| LinearSVC | 0.9477 | 0.9790 | 0.9631 | 0.9819 | 0.9547 | 0.9681 | `[[1631,35],[90,1897]]` |
| NB | 0.9108 | 0.9502 | 0.9301 | 0.9567 | 0.9220 | 0.9390 | `[[1583,83],[155,1832]]` |

## Preliminary verdict

No quantitative shortcut fraction, external-data generalization result, or Phase C data recommendation can be responsibly concluded from E1 alone. The remaining experiments are required to distinguish lexical/content signal from publisher and formatting artifacts.

## Reproduction commands

Run from the repository root with the project environment active:

```powershell
& .venv\Scripts\python.exe -B experiments\phase_b\run_e1_baseline.py
& .venv\Scripts\python.exe -B experiments\phase_b\run_e2_top_features.py
& .venv\Scripts\python.exe -B experiments\phase_b\run_e3_marker_stripping.py
& .venv\Scripts\python.exe -B experiments\phase_b\run_e4_probes.py
& .venv\Scripts\python.exe -B experiments\phase_b\run_e5_short_input.py
& .venv\Scripts\python.exe -B experiments\phase_b\run_e6_external.py
```
