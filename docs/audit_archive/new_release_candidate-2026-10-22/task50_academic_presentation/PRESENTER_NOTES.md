# TruthScan Academic Presentation — Presenter Notes

## Slide 1 — TruthScan: Fake News Detector

Introduce TruthScan as an academic software project. State immediately that Track A is the existing Fake/Real article classifier and Track B is only a synthetic claim-verification contract prototype.

## Slide 2 — The problem TruthScan addresses

Explain that the application produces a learned signal from article text. It does not consult live sources or establish factual truth. Human review and context remain necessary.

## Slide 3 — Scope

Highlight the work that can be demonstrated safely: application architecture, validation, guarded loading, documentation, and synthetic contract behavior. Make clear that training, dataset acquisition, and deployment approval are outside this presentation.

## Slide 4 — Actual production architecture

Walk from the browser through FastAPI and the API router into preprocessing and prediction. Explain that artifact verification occurs before model deserialization. Point out the dashed Track B separation: no production route or import connects it.

## Slide 5 — Fake/Real pipeline

Describe request validation, spaCy preprocessing, model prediction, probability aggregation, and the response. Emphasize that a calibrated probability is a model output, not a factual certainty.

## Slide 6 — Ensemble and preprocessing

Name the five model classes visible in `predictor.py`. Explain that the vectorizer and calibrated models are loaded from the bundle only after the verification boundary. Do not claim the historical files are authenticated merely because the code expects them.

## Slide 7 — Reported evaluation evidence

Say “README-reported” when discussing the accuracy bars. Explain that prior scores were not rerun for this presentation and that unresolved dataset provenance, artifact authenticity, and configuration history limit what those numbers prove.

## Slide 8 — Security and trust safeguards

Separate source-code safeguards from trust evidence. The project can reject missing or mismatched evidence, but it still needs independently provisioned expected digests, public keys, rights records, environment evidence, and owner release approval.

## Slide 9 — Synthetic Track B prototype

Explain the three semantic outcomes: `SUPPORTED`, `REFUTED`, and `INSUFFICIENT_EVIDENCE`. The prototype has no retriever, model, real evidence, or production route. Never translate its outcomes into Fake or Real.

## Slide 10 — Demonstrated work

Credit the source audits, synthetic contract tests, UI smoke checks, and release planning. Clarify that these strengthen readiness evidence but do not close the real-data or release gates.

## Slide 11 — Limitations and ethics

Use this slide to answer readiness questions directly. Dataset rights, artifact provenance, trusted release roots, environment reproducibility, owner approval, and deployment review remain open. Avoid presenting model output as a factual verdict.

## Slide 12 — Conclusion

Close with the balanced result: TruthScan is presentable as an academic software demonstration, while a real-data release or public claim-verification service requires further evidence and authorization.
