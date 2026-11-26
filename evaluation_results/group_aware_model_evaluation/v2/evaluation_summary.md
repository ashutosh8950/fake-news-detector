# Group-aware model evaluation — corrected v1 report package

This namespace packages the existing Task 10 evaluation; it does not retrain models.
The experiment used the explicitly documented `regex_fallback_experimental` preprocessing because the active environment has no importable `spacy` package and no `en_core_web_sm` model. It is therefore not production-equivalent.

The primary `all_keys_v1` and sensitivity `body_combined_only_v1` policies use distinct approved test populations. The candidates were Logistic Regression, Decision Tree, Gradient Boosting, Multinomial Naive Bayes, and Linear SVC. Selection used method-selection macro-F1, with balanced accuracy and model key as tie-breakers. Decision Tree was selected for both policies. A fixed sigmoid calibrator was fitted only on `final_calibration`; outer-test metrics were then computed once.

Metrics use class 0 = Fake and class 1 = Real. PR-AUC treats Real as positive. Confusion matrices use rows and columns in `[Fake, Real]` order. The saved predictions independently reproduce the metrics in `outer_test_metrics.json`, and the matrices in this namespace were independently reconstructed from those predictions.

Primary calibrated outer-test results: accuracy 0.9647, macro-F1 0.9645, balanced accuracy 0.9654, ROC-AUC 0.9654, PR-AUC 0.9588, log loss 0.1551, Brier score 0.0342, ECE 0.0134; matrix `[[1622, 44], [85, 1902]]`.

Sensitivity calibrated outer-test results: accuracy 0.9766, macro-F1 0.9765, balanced accuracy 0.9765, ROC-AUC 0.9765, PR-AUC 0.9697, log loss 0.1107, Brier score 0.0228, ECE 0.00135; matrix `[[1576, 40], [43, 1894]]`.

Uncertainty uses 100 group-bootstrap replicates with seed 42 and connected-component groups as the resampling unit. This is a limited empirical interval, not a guarantee. The two policies are not a controlled head-to-head comparison because their grouping rules and test populations differ. Dataset-specific language, source construction, temporal effects, publisher effects, and adversarial generalization remain unresolved.

Task 10 identified a serialization bug: the original writer requested `confusion_matrix` while the metric object stored `confusion_matrix_class_order_0_fake_1_real`, producing null values. This package reconstructs the matrices from saved prediction labels and verifies equality with the saved metrics. Source bytes, row counts, ordered schemas, labels, and schema fingerprints were independently recomputed.

Production-equivalent retraining is blocked pending installation and validation of the required spaCy package and `en_core_web_sm` model. No installation or download was attempted.
