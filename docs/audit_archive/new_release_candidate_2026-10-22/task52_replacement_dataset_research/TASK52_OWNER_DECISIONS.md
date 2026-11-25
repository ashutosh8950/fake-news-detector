# Task 52 — Owner Decisions Required

This checklist records decisions needed before any replacement dataset can move beyond research. No decision is made by this task.

## Candidate and task scope

- [ ] Decide whether to authorize a **research-only FakeNewsNet PolitiFact assessment**.
- [ ] Select one exact release/repository revision if the assessment proceeds.
- [ ] Decide whether Track A must remain article-level Fake/Real without any proxy-label conversion.
- [ ] Decide whether a separate source-reliability or topic-specific health-misinformation task is acceptable instead of general Fake/Real.
- [ ] Keep NELA-GT, FEVER, and source-reliability labels out of Track A unless a new scientific target is explicitly approved.

## Rights and provenance

- [ ] Obtain an authoritative acquisition path and exact source revision.
- [ ] Record source, release, file identity, acquisition date, and cryptographic digests after authorization.
- [ ] Identify rights for underlying article text, URLs, metadata, images, comments, tweets, and other third-party material separately from the package license.
- [ ] Confirm authority of the party granting or describing the relevant permission.
- [ ] Obtain qualified rights review for training, public inference, commercial use, model-weight distribution, and raw/transformed-data redistribution.
- [ ] Record attribution, share-alike, privacy, deletion, takedown, and retention requirements.
- [ ] For FakeNewsNet specifically, resolve the repository’s stated Twitter privacy and publisher-copyright limitations before retaining or redistributing any component.

## Scientific and evaluation approval

- [ ] Approve label semantics and refuse any unsupported collapse to Fake/Real.
- [ ] Approve source/publisher-grouped splits.
- [ ] Approve exact and near-duplicate detection and syndicated-content handling.
- [ ] Approve time-aware validation and test design.
- [ ] Approve training-only preprocessing and calibration.
- [ ] Require source-only and text-only baselines to expose shortcut learning.
- [ ] Define metrics, abstention coverage, out-of-domain tests, and the wording allowed for results.

## Public website and operations

- [ ] Decide whether public inference is in scope at all.
- [ ] Define supported languages, domains, article formats, and unsupported cases.
- [ ] Approve non-definitive user messaging and abstention behavior.
- [ ] Define privacy, retention, deletion, and abuse-handling policy for visitor-submitted text.
- [ ] Approve security controls for oversized input, malicious content, rate abuse, model extraction, and logging.
- [ ] Confirm that the application will not present a model output as verified fact.

## Build and release gates

- [ ] Resolve trusted model-artifact provenance and independently authenticated release roots.
- [ ] Resolve hash-pinned dependency and clean-install evidence for the target CI platform.
- [ ] Create a new candidate-only build namespace; do not overwrite historical artifacts.
- [ ] Require a signed or independently attested manifest binding source revision, dataset identity/digests, configuration, environment, and artifact hashes.
- [ ] Obtain explicit approval for local academic use, public hosting, commercial use, model distribution, and data redistribution separately.

## Hard stop

Until the selected candidate has an exact identity, reviewed rights scope, approved label policy, leakage-resistant evaluation plan, trusted build evidence, and explicit release authorization, the project must not acquire the dataset, train or calibrate models, create artifacts, enable inference, host the model publicly, or redistribute data.

Current decision: **UNDECIDED**.  
Current recommendation: **FakeNewsNet PolitiFact is a research-only lead for further assessment, not an approved dataset.**
