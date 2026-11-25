# Task 43 — Proposed API and UI Contracts

These are design contracts only. They were not implemented or tested against real data.

## Track A article contract

`POST /api/v2/article/analyze`

Request:

```json
{"title":"optional headline","text":"article text"}
```

Response retains the current semantic family:

```json
{
  "track":"article_classifier",
  "task":"fake_vs_real_news",
  "label":"FAKE|REAL",
  "probability_real": 0.0,
  "confidence": 0.0,
  "disclaimer":"Model signal; not factual verification.",
  "model_version":"authenticated release identifier"
}
```

The response must not imply that confidence is factual certainty or that live sources were checked.

## Track B claim contract

`POST /api/v2/claims/verify`

Request:

```json
{"claim":"text of a checkable claim","evidence_mode":"required|optional"}
```

Response:

```json
{
  "track":"claim_verifier",
  "task":"fever_claim_verification",
  "outcome":"SUPPORTED|REFUTED|INSUFFICIENT_EVIDENCE",
  "score":0.0,
  "evidence":[{"source_id":"stable reference","title":"display title","snippet":"approved excerpt or reference"}],
  "limitations":["Evidence scope and model limitations"],
  "disclaimer":"Claim-verification demonstration; not an authoritative fact-check."
}
```

`INSUFFICIENT_EVIDENCE` is a first-class result, not a fallback to `FAKE` or `REAL`. If evidence references cannot be validated or the Track B model is unavailable, return a disabled/unavailable response rather than an inferred outcome.

## UI behavior

Track A keeps the current article form and clearly labels results as model signals. Track B, if authorized later, gets a distinct “Claim verification demo” view with separate input language, outcome colors, evidence references, source links where permitted, and a persistent disclaimer. It must not reuse the Track A Fake/Real donut, model cards, or confidence wording.

## Error and readiness contract

Both routes should return explicit `disabled`, `not_ready`, or `insufficient_evidence` states. A healthy web server is not evidence that a track’s model or rights gates passed. Track B must remain disabled until its own artifact and release checks pass.
