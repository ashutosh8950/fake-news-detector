# Task 45 — Security Findings

## Finding F-01 — Evidence-free positive outcomes

- Severity: **Medium** for the prototype contract; higher only if reused in a live service.
- Evidence: `validate_response` checks that `evidence` is a list and only rejects evidence when the outcome is `INSUFFICIENT_EVIDENCE`. It does not require evidence for `SUPPORTED` or `REFUTED`.
- Verification: direct synthetic response with `outcome="SUPPORTED"` and `evidence=[]` returned successfully; the equivalent `REFUTED` response also returned successfully.
- Impact: a caller could construct a positive semantic result without supporting evidence, contrary to the documented evidence-display contract.
- Recommended remediation: require at least one validated evidence object for `SUPPORTED` and `REFUTED`; retain an empty list requirement for `INSUFFICIENT_EVIDENCE`.

## Finding F-02 — Evidence item shape is not validated

- Severity: **Medium** for the prototype contract; higher if reused behind an API.
- Evidence: `validate_response` checks only that `evidence` is a list. `render_mock_ui` assumes every item has `.get`.
- Verification: `evidence=[1]` was accepted by validation and caused `render_mock_ui` to raise `AttributeError`.
- Impact: malformed response data can cause an unhandled failure rather than a safe contract error.
- Recommended remediation: require each item to be a mapping with an allowlisted schema and string fields; reject malformed entries before rendering.

## Finding F-03 — Missing hostile-string regression test

- Severity: **Low**.
- Evidence: source inspection shows `html.escape` is applied to rendered source IDs, disclaimers, and limitations, but the test only checks ordinary synthetic strings.
- Verification: no hostile-string test exists in `test_synthetic_claim_api.py`.
- Recommended remediation: add synthetic `<script>`/attribute payload tests and assert escaped output. No production change is needed.

## Boundary result

No production route, model, dataset, network, artifact, or deployment path was found. The findings are confined to the isolated prototype and were not fixed during this audit, as required.
