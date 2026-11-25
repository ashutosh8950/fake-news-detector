# Presentation and Screenshot Checklist

These are capture suggestions only. No screenshots are claimed to have been captured.

## Suggested visuals

- Existing TruthScan homepage showing the article Fake/Real workflow.
- Repository structure showing `app.py`, `routers/`, `frontend/`, preprocessing, predictor, and audit directories.
- Architecture diagram from `TRUTHSCAN_ARCHITECTURE.md`.
- Candidate workflow diagram from `CANDIDATE_BUILD_WORKFLOW.md`.
- Source excerpt showing the production route and artifact-verification boundary.
- Existing audit report index showing provenance and release blockers.
- Task 44 `UI_MOCKUP.html` with the synthetic-only label and disabled control.
- Task 48 case matrix or test-results report, with the browser-unverified limitation visible.
- Security/trust model showing independent trust-root requirements.

## Capture rules

- Use only local, approved screens and synthetic fixtures.
- Redact credentials, environment variables, personal paths where appropriate, and any sensitive logs.
- Do not show model binary contents, dataset rows, private keys, or unverified source claims as proof.
- Label every synthetic screen as synthetic and every prior result as reported or independently inspected as appropriate.
- Do not capture or publish a production dashboard in a way that implies deployment approval.

## Presenter checks

- Explain that Track A is Fake/Real classification, not factual verification.
- Explain that Track B is not registered with production.
- State that no candidate release or public deployment is approved.
- Keep the owner decisions and unresolved evidence gaps visible in the closing slide.
