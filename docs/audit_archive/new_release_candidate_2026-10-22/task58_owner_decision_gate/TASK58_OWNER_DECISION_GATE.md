# TruthScan — Task 58 Owner Decision Gate

**Status:** `PENDING OWNER RESPONSE`
**Prepared:** 2026-10-27
**Purpose:** record project-scope decisions before any rights inquiry, dataset acquisition, model work, or release activity.

## How to use this record

The owner should select one option in each decision area and record any conditions or reviewer names. No option below grants rights, authorizes acquisition, permits model loading/training, or approves deployment. The Task 56 PolitiFact-Oslo inquiry remains a draft and unsent.

The underlying evidence is drawn from the Task 57 blocker register and critical-path memo, the three Task 56 documents, `MODEL_RELEASE_PREREQUISITES.md`, the Task 27 provenance records, the historical evidence trace, and the dependency validation reports. Prior report findings are identified as inherited evidence; they are not treated as newly reproduced experiments in this decision gate.

## Decision 1 — Intended use

Select exactly one primary scope, or record that the project is paused.

| Choice | Consequence and boundary | Owner response |
|---|---|---|
| **Academic/non-commercial demonstration** | Permits planning and, only after separate gates, a bounded research demonstration. It does not authorize public inference, commercial use, weight release, or data redistribution. | **PENDING OWNER DECISION** |
| **Public, non-commercial website** | Requires explicit permission for public visitor-submitted inference, privacy/retention controls, security and abuse controls, reproducible build evidence, trusted artifacts, authorized evaluation, and deployment approval. | **PENDING OWNER DECISION** |
| **Commercial-capable product** | Adds commercial-use rights, operational controls, model/weight distribution decisions, and a higher release-review scope. No commercial permission is currently established. | **PENDING OWNER DECISION** |
| **Local portfolio demonstration only, predictions disabled until clearance** | Allows documentation, UI, synthetic Track B work, and model-free readiness checks while keeping genuine Track A inference unavailable. This is the safest current option. | **PENDING OWNER DECISION** |
| **Pause dataset-dependent work** | Leaves the application fail-closed and stops rights/data/model work until the owner supplies a direction. | **PENDING OWNER DECISION** |

Selecting an intended use only defines the target scope. It does not grant rights or authorize deployment.

## Decision 2 — Dataset rights pathway

Select one path for the next research direction.

| Choice | Consequence and boundary | Owner response |
|---|---|---|
| **Pursue written permission for PolitiFact-Oslo** | Approve owner review of the Task 56 draft and, if the owner later authorizes it, sending through an appropriate official channel. The inquiry must ask separately about full text, metadata, third-party sources, archives, training, public inference, commercial use, weights, and redistribution. No acquisition occurs from this choice alone. | **PENDING OWNER DECISION** |
| **Investigate another candidate** | Select a replacement only after documenting its article-level label suitability, exact identity, provenance, and rights pathway for the chosen intended use. This does not authorize acquisition. | **PENDING OWNER DECISION** |
| **Pause dataset-dependent work** | Keep the existing local dataset and all candidate datasets blocked. Continue only safe documentation, synthetic demonstrations, and model-free verification. | **PENDING OWNER DECISION** |

The Task 56 inquiry remains **unsent**. No rights holder has been contacted by this task.

## Decision 3 — Public inference and model distribution

Record `PENDING OWNER DECISION` for every item until the owner explicitly answers.

| Question | Owner response |
|---|---|
| Is public analysis of visitor-submitted articles required? | **PENDING OWNER DECISION** |
| Is offline-only evaluation or a local portfolio demonstration sufficient? | **PENDING OWNER DECISION** |
| Will trained weights or checkpoints be distributed? | **PENDING OWNER DECISION** |
| Will raw or transformed datasets be redistributed? | **PENDING OWNER DECISION** |
| Is commercial use in scope now or later? | **PENDING OWNER DECISION** |
| May social-media content, images, or archived copies be excluded even if article-text rights are obtained? | **PENDING OWNER DECISION** |
| Who is accountable for reviewing rights responses and accepting restrictions? | **PENDING OWNER DECISION** |

Each “yes” expands the evidence required. A “no” does not authorize the remaining uses.

## Decision 4 — Release policy

### Recommended policy

Maintain **`NO-GO` for public Fake/Real inference** until every mandatory gate below is cleared with evidence and explicit approval. Keep the current application fail-closed when trusted artifacts are unavailable.

### Minimum release gates

1. **Dataset rights:** written or otherwise qualified rights determination covering the exact retained fields and intended use.
2. **Dataset provenance:** immutable source/revision, acquisition chain, transformation record, local digests, and authenticated source-to-local mapping.
3. **Trusted artifact provenance:** independently authenticated manifest or attestation, trust root, compatibility evidence, and owner-approved artifact identity.
4. **Reproducible dependencies:** approved target platform/source, hash-enforced dependency lock, clean installation, `pip check`, and relevant test evidence.
5. **Authorized evaluation:** owner-approved target semantics, duplicate/source/temporal leakage controls, fresh evaluation, calibration/abstention results, and limitations review.
6. **Security and privacy:** retention/deletion policy, privacy review, input/output protections, rate limits, monitoring, incident response, and abuse controls.
7. **Configuration consistency:** written resolution or retirement of the historical `production_switch` mismatch and an unambiguous new release configuration.
8. **Final authorization:** explicit owner and deployment approval for the exact artifact, scope, environment, and public behavior.

No current evidence clears these gates. The `production_switch` discrepancy does not currently control runtime selection according to the inspected historical evidence, but it remains a release-state ambiguity that requires an owner decision.

## Decision 5 — Time and effort

The following are approximate engineering/review estimates after prerequisites are approved. They are not promises that permission will be granted and exclude external waiting time.

| Work stage | Approximate effort | Assumptions and external dependency |
|---|---:|---|
| Owner scope decision and package review | 1–3 hours | Owner is available and can select a direction. |
| Candidate-specific rights/provenance review | 4–12 hours | Requires a response or authoritative terms; response time is unknown. |
| Approved target environment and hash-enforced dependency evidence | 4–10 hours | Requires an approved package mirror or retained distributions. |
| Leakage-aware evaluation plan and manifests | 8–16 hours | Requires authorized data and an approved target definition. |
| Fresh evaluation and limitations report | 8–16 hours | Requires approved data, environment, and evaluation protocol. |
| Controlled artifact build and independent trust-root evidence | 8–16 hours | Requires approved inputs, build environment, and attestation authority. |
| Security/privacy/monitoring/abuse review | 8–20 hours | Requires reviewer and deployment-owner participation. |
| Final release preparation | 2–6 hours | Requires every prior gate and explicit approval. |

External waiting time is **unknown** for rights-holder responses, qualified review, package-source approval, trust-root provisioning, and deployment authorization. If a gate fails, later stages must not begin.

## Critical-path consequence

```text
Owner selects scope and direction
  -> rights/provenance review
  -> immutable approved dataset and rights record
  -> approved reproducible environment
  -> authorized leakage-aware evaluation
  -> independently trusted artifact build
  -> security/privacy/operations review
  -> explicit final release approval
```

The owner’s first response should therefore answer Decisions 1–3 and identify the accountable rights/release reviewer. Until then, the recommended operational state is local portfolio demonstration with predictions disabled.

## Evidence limitations

- Task 56 and Task 57 provide documentation and prior report evidence, not permission grants.
- The Task 55 source register records public-source access on 2026-10-27; this task did not contact rights holders or re-run external research.
- The historical 98.44% result remains reported evidence with unresolved provenance and generalization limits.
- The current dependency lock remains hashless and clean-install reproducibility is not established.
- No decision in this document approves a dataset, model artifact, public inference, or deployment.

