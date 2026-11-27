# Task 38 — Validation Report

## Result

**CONDITIONAL PASS for the targeted rights review and owner gate.** No owner
authorization or acquisition approval was inferred. The existing dataset
remains `NO_GO_BLOCKED_INSUFFICIENT_EVIDENCE`.

## Files created

- `TASK38_LIAR_RIGHTS_REVIEW.md`
- `TASK38_FAKEDDIT_RIGHTS_REVIEW.md`
- `TASK38_TECHNICAL_SUITABILITY_COMPARISON.md`
- `TASK38_OWNER_AUTHORIZATION_TEMPLATE.json`
- `TASK38_EVIDENCE_REGISTER.json`
- `TASK38_VALIDATION_REPORT.md`

All files are confined to
`evaluation_results/new_release_candidate_2026-10-22/task38_targeted_rights_review/`.

## Sources checked

Read-only public sources were checked on 2026-10-22, including the official
LIAR archive index, original LIAR paper, LIAR dataset-card documentation,
PolitiFact’s official copyright terms, the official Fakeddit repository and
project page, the original Fakeddit paper, and Reddit’s official Public Content
Policy. A third-party LIAR README mirror was used only to record its displayed
research-only/copyright language and was explicitly not treated as an
authenticated license grant.

## Validation checks

- All three new JSON files parsed successfully with the standard Python JSON parser.
- Every substantive rights conclusion in the evidence register has a URL,
  source type, retrieval date, supported conclusion, and limitation.
- Activity classifications do not exceed the cited terms: no commercial,
  hosting, model-distribution, or raw-redistribution activity is marked
  supported.
- Owner decisions and authorization fields remain `PENDING`/`null`.
- No candidate is described as approved or authorized.
- LIAR and Fakeddit are explicitly distinguished from the existing binary
  article-level TruthScan task.
- No dataset was downloaded, cloned, scraped, or processed; no model was
  loaded, trained, calibrated, evaluated, or generated.
- No production code, secure preflight, trust root, release gate, dataset, or
  prior report was modified.

## Git state

Initial and final HEAD: `8c41ae005f4bee178a2b0104cb29049f00182081`.
The pre-existing modified and untracked files were preserved. No commit, push,
deploy, reset, clean, or history modification occurred.

## Limitations and next decision

The public records do not establish complete downstream rights for either
candidate. Qualified legal or rights-holder confirmation remains necessary,
especially for PolitiFact statements and Reddit text, comments, images,
deletion handling, and commercial use. The owner must choose whether to
continue LIAR-only, Fakeddit-only, both, stop pending clarification, or propose
another candidate. Research authorization must remain separate from acquisition,
processing, training, model distribution, hosting, and deployment authorization.
