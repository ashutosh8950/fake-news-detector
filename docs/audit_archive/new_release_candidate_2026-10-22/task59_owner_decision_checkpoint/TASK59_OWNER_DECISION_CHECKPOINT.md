# TruthScan — Task 59 Owner Decision Checkpoint

**Status:** `PENDING OWNER RESPONSE`
**Checkpoint date:** 2026-10-27

## Current recommendation

**`NO-GO` for public Fake/Real inference.** The Task 57 register reports that no release blocker is cleared, and the Task 58 gate records that intended use, dataset direction, public inference, distribution, and commercial scope remain unanswered.

The application should remain fail-closed and unavailable for genuine inference until the relevant rights, provenance, artifact, environment, evaluation, security, and approval gates are satisfied.

## Owner decisions still pending

| Decision | Choices to record | Current state |
|---|---|---|
| Intended-use scope | Academic/non-commercial demonstration; public non-commercial website; commercial-capable product; local portfolio demonstration with predictions disabled; pause. | **PENDING OWNER DECISION** |
| Dataset pathway | Pursue written permission for PolitiFact-Oslo; assess another candidate with a documented label and rights pathway; pause dataset-dependent work. | **PENDING OWNER DECISION** |
| Inference scope | Public visitor-submitted article analysis or offline-only evaluation/demonstration. | **PENDING OWNER DECISION** |
| Model distribution | Distribute trained weights/checkpoints or keep them private. | **PENDING OWNER DECISION** |
| Dataset distribution | Redistribute raw/transformed data or retain it privately under approved restrictions. | **PENDING OWNER DECISION** |
| Commercial scope | Commercial use now/later or no commercial use. | **PENDING OWNER DECISION** |
| Accountability | Name the owner and qualified reviewer for rights, artifact trust, evaluation, security/privacy, and final release approval. | **PENDING OWNER DECISION** |

No choice is inferred from prior reports. The Task 56 PolitiFact-Oslo inquiry remains a draft and unsent.

## Activities prohibited until prerequisites and approvals exist

The following must remain on hold:

- Sending the Task 56 rights inquiry or contacting rights holders.
- Acquiring, scraping, extracting, or inspecting candidate datasets or article text.
- Training, fine-tuning, calibrating, evaluating, or running genuine inference.
- Loading historical model artifacts or treating them as trusted.
- Creating or activating a new production model bundle.
- Enabling public Fake/Real inference or deploying the website.
- Distributing model weights, raw data, or transformed data.
- Resolving the `production_switch` mismatch by assumption.

These restrictions follow the unresolved blockers recorded in Task 57, including dataset rights/provenance, artifact authenticity, dependency reproducibility, authorized evaluation, security/privacy controls, and final release approval.

## Safe work that may continue without owner decisions

The following bounded work does not require dataset acquisition, model loading, training, evaluation, inference, or deployment:

- Maintain documentation and the owner decision record.
- Run or extend synthetic-only Track B contract tests and demonstrations.
- Run model-free readiness and unavailable-model smoke checks that assert fail-closed behavior.
- Improve or test frontend loading, validation, error, and unavailable-model states without claiming a prediction.
- Perform static review of API contracts, Track A/Track B separation, security handling, and release documentation.
- Review CI configuration and document dependency-source limitations without installing packages or weakening verification.
- Prepare academic presentation materials that clearly label historical results as reported evidence and Track B as synthetic-only.

Safe work must not be used to imply that rights, artifacts, reproducibility, evaluation validity, or public release approval has been established.

## Decision recording checklist

The owner should later complete each item explicitly:

- [ ] **PENDING OWNER DECISION:** Intended-use scope selected.
- [ ] **PENDING OWNER DECISION:** Dataset pathway selected.
- [ ] **PENDING OWNER DECISION:** Public inference or offline-only scope selected.
- [ ] **PENDING OWNER DECISION:** Model-weight distribution decision recorded.
- [ ] **PENDING OWNER DECISION:** Raw/transformed-data redistribution decision recorded.
- [ ] **PENDING OWNER DECISION:** Commercial-use decision recorded.
- [ ] **PENDING OWNER DECISION:** Rights reviewer appointed.
- [ ] **PENDING OWNER DECISION:** Artifact/release reviewer appointed.
- [ ] **PENDING OWNER DECISION:** Security/privacy reviewer and deployment owner identified.
- [ ] **PENDING OWNER DECISION:** PolitiFact-Oslo inquiry approved, replaced with another documented candidate, or declined.

No checkbox is complete in this checkpoint.

## Stop condition

Do not initiate another dataset, model, artifact, evaluation, or release workstream that depends on the unresolved owner decisions above. Wait for the owner’s explicit response, then update the decision gate before taking any dependent action.

