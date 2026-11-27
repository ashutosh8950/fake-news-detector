# Task 46 — Test Results

## Exact command

`python -m unittest discover -s evaluation_results/new_release_candidate_2026-10-22/task44_synthetic_prototype -p "test_*.py" -v`

## Result

**12 passed, 0 failed, 0 skipped.**

Tests covered:

1. Valid synthetic `SUPPORTED` response.
2. Valid synthetic `REFUTED` response.
3. Valid empty-evidence `INSUFFICIENT_EVIDENCE` response.
4. Empty evidence rejected for `SUPPORTED`.
5. Empty evidence rejected for `REFUTED`.
6. Integer, null, malformed, missing-snippet, extra-field evidence rejected.
7. Empty and whitespace-only evidence text rejected.
8. Unknown outcomes and extra response fields rejected.
9. Hostile HTML/script/attribute strings escaped as inert text.
10. Invalid response data rendered as a controlled error state.
11. Original all-outcome, conversion, request, and refusal tests continued to pass.
12. Production/default mode refusal continued to pass.

No test used real data, models, network services, or production routes.
