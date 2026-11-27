# Task 53 — Blockers and Owner Decisions

## Current blockers

1. **Exact revision and reproducible source mapping:** identify an immutable FakeNewsNet PolitiFact revision and preserve an authenticated manifest; the official README’s “current up-to-date version” wording is not enough.
2. **Article-text authority:** determine whether the required PolitiFact and other publisher text may be collected, retained, transformed, and used for training.
3. **Social-data authority:** decide whether tweet IDs alone are needed and whether any recollection or social features are permitted under current platform terms. Do not retain user data by default.
4. **Downstream model scope:** obtain qualified review or written permission for internal research, public inference, commercial use, model-weight distribution, and raw/transformed-data redistribution separately.
5. **Scientific protocol:** approve a label policy and leakage-resistant evaluation plan before treating results as evidence of generalization.
6. **Existing release blockers:** the current project still lacks authenticated provenance for `Fake.csv`/`True.csv`, trusted historical model artifacts, reproducible dependency evidence, and public deployment authorization.

## Owner decisions required

- [ ] Authorize or decline a **research-only rights/provenance inquiry** for one identified FakeNewsNet PolitiFact revision.
- [ ] Define the intended scope: academic-only/internal evaluation, non-commercial public demonstration, commercial use, model-weight distribution, and raw/transformed-data redistribution.
- [ ] Appoint the owner or qualified reviewer responsible for accepting rights evidence and deciding whether it is sufficient.
- [ ] Decide whether the project may retain article text, only metadata/URLs, or neither until written permission exists.
- [ ] Approve a label policy that documents exactly how PolitiFact ratings become any binary research target; do not assume all ratings map to `fake` or `real`.
- [ ] Approve source-grouped, duplicate-resistant, time-aware evaluation criteria before any future training.

## Decision gate

Until the owner decisions and evidence above exist, FakeNewsNet PolitiFact remains `POTENTIALLY VIABLE — FURTHER RIGHTS REVIEW REQUIRED` and `RESEARCH LEAD — NOT APPROVED`. Do not acquire data, reconstruct article text, train or calibrate models, create artifacts, enable inference, distribute weights, or deploy the public site.

## Smallest next action

Record the owner’s decision on the first checkbox and the intended-use scope. If the inquiry is authorized, request the exact revision and written answers on retention, training, public inference, model weights, attribution, deletion, and redistribution. If it is declined or unresolved, stop Option B for this candidate and keep the application fail-closed.

