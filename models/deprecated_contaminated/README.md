# Deprecated contaminated model artifacts

These model artifacts were trained before Phase 1 established its rigorous held-out test split.

The later Phase 1 held-out set contains 3,653 rows. A reconstruction of the training procedure used for these artifacts confirmed that 2,740 rows—75% of the Phase 1 held-out set—were present in their training data. Their evaluation results are therefore contaminated and unreliable.

Do not use these artifacts for evaluation or comparison. They must not be loaded by `predictor.py` or by any other script going forward.

The files are retained here for auditability and have been moved rather than deleted.
