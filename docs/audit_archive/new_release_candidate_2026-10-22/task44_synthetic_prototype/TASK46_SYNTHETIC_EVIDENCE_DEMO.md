# Synthetic Evidence-to-Verdict Demonstration

## Purpose

`synthetic_evidence_demo.py` is a small, deterministic Track B demonstration. It uses three hand-authored examples and sends their response objects through the existing `validate_response` contract.

Every example is marked `synthetic: true`. Evidence identifiers use `SYNTHETIC-ONLY-*` and `synthetic://` placeholders. They are not citations, real sources, retrieved evidence, or factual conclusions.

## Run

From this directory:

```text
python synthetic_evidence_demo.py
```

The runner prints JSON containing one example for each permitted outcome:

- `SUPPORTED`: supplied synthetic evidence is explicitly written to support the assigned fixture outcome.
- `REFUTED`: supplied synthetic evidence is explicitly written to refute the assigned fixture outcome.
- `INSUFFICIENT_EVIDENCE`: the evidence list is empty, so the contract abstains.

Run the demonstration tests with:

```text
python -m unittest -v test_synthetic_evidence_demo.py
```

Run the complete isolated prototype suite with:

```text
python -m unittest -v test_synthetic_claim_api.py test_synthetic_evidence_demo.py
```

## What this demonstrates

- A hand-authored claim, evidence card, assigned outcome, and rationale can be represented together.
- The existing response validator enforces the three allowed outcomes and evidence requirements.
- Missing evidence produces `INSUFFICIENT_EVIDENCE` rather than a successful verdict.
- Invalid evidence cannot be silently converted into `SUPPORTED` or `REFUTED`.
- Track B remains a separate claim-verification contract and is not converted to Track A `Fake`/`Real`.

## What this does not demonstrate

- No model predicts the outcome.
- No evidence is retrieved from Wikipedia, the web, FEVER, or any external service.
- No source is authenticated and no statement is verified as true or false.
- Metadata validation does not establish source authenticity, licensing, or evidence truthfulness.
- This is not a FastAPI route, production feature, public fact-checker, or release approval.
