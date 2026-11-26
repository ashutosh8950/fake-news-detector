# Production-equivalent group-aware evaluation

This is a fresh evaluation using the unchanged production `preprocessor.preprocess` path. No regex fallback was used. The environment was Python 3.11.9, spaCy 3.8.16, and `en_core_web_sm` 3.8.0; the model loaded with parser and NER disabled.

The approved primary `all_keys_v1` and sensitivity `body_combined_only_v1` manifests were used as separate evaluation protocols. Their test populations differ and scores are not a controlled head-to-head comparison.

Candidates were Logistic Regression, Decision Tree, Gradient Boosting, Multinomial Naive Bayes, and Linear SVC. Selection was frozen as method-selection macro-F1, then balanced accuracy, then model key. Decision Tree was selected for both policies. TF-IDF and SVD were fitted only on proper-fit. Sigmoid calibration was fitted only on final-calibration. Outer-test metrics were accessed after those decisions were frozen.

Class convention: 0 = Fake, 1 = Real. PR-AUC uses Real as the positive class. Confusion matrices use rows and columns `[Fake, Real]`. ECE uses ten uniform bins. Uncertainty uses 100 connected-component group-bootstrap replicates with seed 42.

## Primary all-key

Selected model: `Decision Tree`. N=3653; accuracy=0.9639; macro-F1=0.9637; balanced accuracy=0.9647; ROC-AUC=0.9647; PR-AUC=0.9582; log loss=0.1567; Brier=0.0349; ECE=0.0133.
Confusion matrix: `[[1622, 44], [88, 1899]]`.

## Sensitivity body/combined-only

Selected model: `Decision Tree`. N=3553; accuracy=0.9738; macro-F1=0.9736; balanced accuracy=0.9743; ROC-AUC=0.9743; PR-AUC=0.9689; log loss=0.1204; Brier=0.0255; ECE=0.0061.
Confusion matrix: `[[1582, 34], [59, 1878]]`.

The 100-replicate bootstrap intervals are empirical and limited. They do not establish real-world, temporal, publisher, adversarial, or deployment robustness. Dataset construction and source-specific language may influence performance.

Independent checks recomputed source provenance, manifest row coverage, inner/outer boundaries, group crossings, confusion matrices, saved outer-test metrics, probability validity, and artifact hashes. Caches and bytecode are excluded from the artifact inventory.
