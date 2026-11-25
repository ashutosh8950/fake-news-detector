# Task 45 — Independent Verification Audit

## Result

**CONDITIONAL PASS for isolation; FAIL for the complete response-evidence contract.** The prototype is isolated from production and the reported eight tests pass, but independent adversarial checks reproduced two contract weaknesses. Track B remains disabled and unapproved.

## Baseline and scope

Initial and final HEAD: `8c41ae005f4bee178a2b0104cb29049f00182081`.

The initial working tree contained pre-existing modifications to `README.md`, `app.py`, `download_models.py`, `frontend/style.css`, `phase2_calibration.py`, `predictor.py`, `routers/api.py`, and `train.py`, plus prior untracked audit work. The same tracked paths remained modified after this audit. No production file was edited.

## Verified implementation claims

- `OUTCOMES` contains exactly `SUPPORTED`, `REFUTED`, and `INSUFFICIENT_EVIDENCE`.
- `validate_request` rejects non-mappings, unexpected/missing fields, empty claims, claims over 4,000 characters, and invalid evidence modes.
- `validate_response` rejects unknown outcomes, wrong track/task identity, invalid score bounds, missing list fields, missing disclaimers, extra fields, and evidence attached to `INSUFFICIENT_EVIDENCE`.
- `run_synthetic_fixture` refuses by default and refuses `environment="production"`; it produces only pre-authored synthetic placeholders.
- `forbid_track_a_conversion` rejects conversion of Track B outcomes to Track A labels.
- `render_mock_ui` escapes rendered source IDs, limitations, and disclaimers. The static HTML mockup is disabled and labels evidence as synthetic.
- The prototype has no FastAPI import, route registration, model/data import, network client, or filesystem operation.
- Repository search found no production reference to `synthetic_claim_api`, `task44_synthetic_prototype`, `claim_verifier`, or `fever_claim_verification`.

## Reproduced gaps

1. `validate_response` accepts `SUPPORTED` or `REFUTED` with `evidence: []`. This violates the stated contract if those outcomes require supporting evidence and permits a misleading positive outcome at the contract layer.
2. `validate_response` accepts evidence entries of arbitrary types, including `1`. `render_mock_ui` then calls `.get` on each entry and raises an unhandled `AttributeError`. The current prototype is not a live API, but this is unsafe malformed-response behavior.
3. The test suite does not cover unsafe source IDs or limitations containing HTML. The renderer does escape source IDs and limitations by inspection, but that property is not regression-tested.

## Not reproduced

No path was found from the prototype to Track A routing, model loading, training, artifact creation, deployment configuration, or production static-file serving. No real data/model operation was attempted.

## Recommendation

Before reusing the contract, add candidate-only tests and a minimal validator fix requiring non-empty, structurally valid evidence for `SUPPORTED` and `REFUTED`, while preserving empty evidence for `INSUFFICIENT_EVIDENCE`. Validate each evidence item’s allowed fields and types, and add HTML-escaping regression tests. Do not expose the prototype or enable Track B until those fixes and the independent rights/release gates are complete.
