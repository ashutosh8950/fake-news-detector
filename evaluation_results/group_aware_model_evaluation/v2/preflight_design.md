# Fresh group-aware evaluation preflight

Status: Gate A passed for split integrity and provenance; production preprocessing reproduction is unavailable in this environment because `spacy` and `en_core_web_sm` are not installed. This experiment therefore uses an explicitly labeled regex-only preprocessing fallback and must not be interpreted as an exact reproduction of the deployed preprocessing pipeline.

## Approved data boundaries

- Class `0`: Fake (`data/Fake.csv`)
- Class `1`: Real (`data/True.csv`)
- Primary policy: `evaluation_results/duplicate_aware/final_v5/primary/`
- Sensitivity policy: `evaluation_results/duplicate_aware/final_v5/body_combined_only/`
- Proper-fit: estimator and TF-IDF/SVD fitting only
- Method-selection: candidate comparison only
- Final-calibration: frozen selected estimator calibration only
- Outer test: one final evaluation, never used for selection or calibration

## Experimental text pipeline

The fallback lowercases text, removes bracketed content, URLs, HTML tags, punctuation, numeric-containing tokens, remaining non-ASCII letters, and collapses whitespace. It concatenates title three times with body, matching the production title weighting, but omits spaCy lemmatization and stop-word removal because the required package/model is unavailable. This discrepancy is recorded and is not a production-pipeline claim.

## Candidate models

Fresh estimators are evaluated independently: Logistic Regression, Decision Tree, Multinomial Naive Bayes, Linear SVC, and Gradient Boosting. The first four use sparse TF-IDF. Gradient Boosting uses a 256-component TruncatedSVD representation fitted on proper-fit only because classic GradientBoostingClassifier does not accept the production sparse TF-IDF matrix without unsafe densification. Random Forest is excluded because it is not part of the production predictor ensemble. The initial 200-tree configuration exceeded a reasonable runtime; the declared rerun uses 50 trees and is labeled reduced-cost.

## Selection and calibration

Candidates are selected by highest method-selection macro-F1 at the declared 0.5 probability/decision threshold, with balanced accuracy and deterministic model-key tie breaks. The selected estimator is frozen after fitting on proper-fit. A single predeclared sigmoid calibration mapping is fitted on final-calibration only and evaluated once on outer test. No outer-test result informs selection.

## Metrics and uncertainty

Accuracy, per-class precision/recall/F1, macro-F1, balanced accuracy, confusion matrix, ROC-AUC, PR-AUC, log loss, Brier score, calibration curves, and ECE are recorded where defined. Group bootstrap intervals use outer-test connected components as the resampling unit, 100 replicates, and seed 42.
