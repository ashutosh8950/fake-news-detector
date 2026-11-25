# Task 57 — Owner Decision and Critical Path

## Go/no-go recommendation

**NO-GO for public Fake/Real release.** The current evidence leaves dataset rights, training inputs, artifact authenticity, dependency reproducibility, evaluation validity, production security, and deployment authorization unresolved. Keep the existing fail-closed behavior.

This is a recommendation based on inspected records, not an owner decision. No historical model artifact should be loaded and no new training or evaluation should begin until the applicable gates below are explicitly approved.

## Minimum owner decisions

1. **Direction:** recover the existing dataset provenance, pursue PolitiFact-Oslo, choose another replacement, or pause article-level release work.
2. **Scope:** academic-only/offline demonstration, public non-commercial inference, commercial use, model-weight distribution, and raw/transformed-data redistribution must be selected separately.
3. **Rights reviewer:** appoint the person or qualified reviewer who can accept or reject rights evidence.
4. **`production_switch`:** define the historical field’s meaning, explain the report/script mismatch, or explicitly retire it for a new release configuration.
5. **Evaluation policy:** approve source grouping, duplicate handling, temporal split, calibration, abstention, and the target-label definition.
6. **Trust root:** approve an independent artifact-manifest signing/attestation root and release-approval owner.
7. **Fallback rule:** decide whether PolitiFact-Oslo is abandoned if full-text or third-party rights cannot be established.

## Critical path

```text
Owner chooses direction and intended-use scope
        |
        v
Rights/provenance inquiry and qualified review
        |
        v
Immutable approved dataset/revision + field-level rights record
        |
        v
Approved target environment + hash-enforced dependency evidence
        |
        v
Owner-approved leakage-aware evaluation protocol
        |
        v
Fresh authorized evaluation and limitations review
        |
        v
New controlled artifact build + independent trust-root attestation
        |
        v
Security/privacy/monitoring/abuse review
        |
        v
Explicit owner deployment and public-release authorization
```

Each arrow is a gate. Synthetic tests and existing fail-closed checks may continue independently, but they do not satisfy the rights, data, artifact, or public-release gates.

## Choices and consequences

### Option A — Continue PolitiFact-Oslo review

The Task 56 draft can be reviewed by the owner and, only after approval, sent through an appropriate official channel. This may clarify text retention, training, public inference, commercial use, weights, redistribution, and third-party rights. It does not guarantee permission, and a PolitiFact response may not cover linked publishers, social content, or archives.

### Option B — Abandon PolitiFact-Oslo if rights remain unresolved

Keep the application fail-closed and select a different candidate only through a new documented rights/provenance assessment. Do not substitute source-reliability labels or claim-level datasets for article truth. The existing local `Fake.csv`/`True.csv` files remain unusable for a defensible new release until their own provenance and rights are recovered.

### Option C — Academic/offline documentation only

Continue the synthetic Track B demonstration, model-free readiness harness, documentation, and presentation work without enabling Track A inference. This improves portfolio readiness but does not produce a real Fake/Real model or public website.

## Approximate effort versus external waiting

These are planning estimates only and do not authorize work:

| Stage | Engineering/review effort after prerequisites | External waiting/dependency |
|---|---:|---|
| Owner scope decision and rights package review | 1–3 hours | Owner availability |
| Candidate rights/provenance evidence assessment | 4–12 hours | Rights-holder response and qualified review; unknown duration |
| Target environment and hash-enforced dependency lock | 4–10 hours | Approved mirror or retained distributions |
| Evaluation manifest and leakage-aware harness | 8–16 hours | Approved dataset and policy |
| Fresh authorized evaluation and report | 8–16 hours | Authorized data and approved environment |
| New controlled artifact build and trust-root evidence | 8–16 hours | Approved build inputs and independent attestation |
| Security/privacy/monitoring/abuse review | 8–20 hours | Reviewer and deployment-owner availability |
| Final release decision and deployment preparation | 2–6 hours | Owner/deployer approval |

The external rights, package-source, trust-root, and approval waiting time is not estimated because the repository contains no evidence supporting a duration. If any gate fails, later engineering stages must stop.

## Conditions before protected activities begin

Before dataset acquisition: owner direction, intended-use scope, candidate identity, rights-review authority, and an approved acquisition plan.

Before training or evaluation: all applicable rights, immutable source/revision, transformation record, approved evaluation protocol, and reproducible target environment.

Before model loading: independently authenticated manifest/trust root, compatibility evidence, and explicit artifact approval. Existing `artifact_contract.py` checks integrity against a supplied manifest but does not itself authenticate the manifest’s origin.

Before public inference or deployment: fresh authorized evaluation, uncertainty/abstention behavior, privacy and retention policy, security/abuse/monitoring evidence, dependency/build evidence, downstream-use permission, and explicit owner deployment authorization.

## Recommended immediate action

The owner should first record the direction and intended-use scope, then decide whether to approve the unsent Task 56 PolitiFact-Oslo inquiry. Until that decision and the resulting evidence exist, the safest path is to keep Track A unavailable for inference and continue only model-free verification and synthetic Track B work.

