# Task 43 — Dual-Track Design

## Track A — Existing TruthScan

Purpose: classify article-like input using the existing fake/real contract. Preserve current behavior as the baseline; do not retrain or release it until dataset provenance, artifact trust, environment, approval, and deployment gates are cleared.

Inputs remain a headline plus article text. Outputs remain model/ensemble predictions with calibrated probability semantics, but all public copy must state that the result is a learned resemblance signal, not factual adjudication. The historical production bundle and current dataset are not a trusted new-build source.

Track A owns `/analyze`, `/analyze/deep`, `/models/info`, health, metrics, its preprocessing, and its artifact namespace.

## Track B — Optional FEVER demonstration

Purpose: demonstrate claim verification against evidence, only if FEVER use is later approved. This is a new prototype and a different task.

FEVER outcomes must remain `SUPPORTED`, `REFUTED`, and `INSUFFICIENT_EVIDENCE` (the source task’s `NOT ENOUGH INFO`). They must not be relabeled as `REAL` and `FAKE`. A claim can be unsupported because evidence is missing, without being false; conversely, a refuted claim is not the same semantic object as a fake news article.

Track B must use separate model/artifact directories, dataset identity, license evidence, preprocessing, grouping and evaluation rules, metrics, route namespace, UI labels, disclaimers, and release approval.

## Shared boundary

The safe shared layer is transport and presentation infrastructure only. Each track should select a typed service by explicit route and contract. A shared `PredictionResult` or generic boolean must not be used across tracks. The FEVER service should return evidence references and an explicit evidence insufficiency state; the article classifier should never manufacture evidence citations.

## Proposed runtime separation

```text
FastAPI app
├── /api/v2/article/analyze        → Track A article classifier
├── /api/v2/claims/verify          → Track B FEVER prototype (disabled until approved)
├── /health and /metrics           → track-aware readiness, no implied model approval
└── separate artifact/license/gate records per track
```

The route names are proposed only; no code change is authorized by this plan. Track B must return unavailable/disabled while its dataset, model, and release gates are unresolved.
