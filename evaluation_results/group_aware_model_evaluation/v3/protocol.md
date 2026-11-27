# Frozen production-equivalent group-aware evaluation protocol

Protocol frozen before training or outer-test metric access.

## Environment and preprocessing

- Interpreter: `C:\Users\gupta\Downloads\FAKE_NEWS_DETECTION\.venv\Scripts\python.exe`
- Python: 3.11.9
- spaCy: 3.8.16
- `en_core_web_sm`: 3.8.0
- Production function: `preprocessor.preprocess(title, text)`
- Loader: `spacy.load("en_core_web_sm", disable=["parser", "ner"])`
- Active pipeline: `tok2vec`, `tagger`, `attribute_ruler`, `lemmatizer`
- Cleaning, title repetition, token filtering, stop-word removal, and lemmatization are delegated to the unchanged production implementation. No fallback preprocessing is permitted.

## Approved data and boundaries

- Primary policy: `all_keys_v1`, approved `final_v5/primary`.
- Sensitivity policy: `body_combined_only_v1`, approved `final_v5/body_combined_only`.
- Proper-fit fits vectorizers, SVD where required, candidate estimators, and the selected estimator.
- Method-selection is used only for candidate selection.
- Final-calibration is used only for the fixed sigmoid calibration mapping.
- Outer-test is accessed only after selection and calibration procedures are frozen.
- Class mapping: `0 = Fake`, `1 = Real`.

## Features and candidate models

TF-IDF is fitted on proper-fit text only with `ngram_range=(1,2)`, `max_features=150000`, `sublinear_tf=True`, `analyzer="word"`, `min_df=2`, and `max_df=0.95`.

Candidates are Logistic Regression (`C=5`, `max_iter=1000`), Decision Tree (`max_depth=None`), Gradient Boosting (`n_estimators=50`, with 256-component TruncatedSVD fitted on proper-fit only), Multinomial Naive Bayes (`alpha=0.01`), and Linear SVC (`C=1`, `max_iter=2000`). Random state is 42 where supported.

Selection is highest method-selection macro-F1, then highest balanced accuracy, then lexicographically smallest model key. Threshold is 0.5.

## Calibration and metrics

A sigmoid calibrator is fit only on final-calibration scores from the selected base estimator. The positive probability is explicitly the probability of class 1 (`Real`). Calibration method is fixed in advance; it is not selected using outer-test data.

Report accuracy, per-class precision/recall/F1, macro-F1, balanced accuracy, confusion matrix with rows and columns `[Fake, Real]`, ROC-AUC, PR-AUC with `Real` positive, log loss, Brier score, and ECE using ten uniform bins on [0,1]. Empty bins are omitted from ECE sums.

Uncertainty uses 100 group-bootstrap replicates, seed 42, resampling complete outer-test connected-component groups. These are empirical intervals with limited replicates, not guarantees.

## Verification

Save source provenance, manifest validation, method-selection metrics, predictions, outer metrics, calibration data, confusion matrices, uncertainty intervals, environment information, and artifact hashes. Exclude caches and bytecode from artifact hashes. Independently recompute metrics from saved predictions and verify numeric confusion matrices and hash consistency.
