# TruthScan FEVER Decision Readiness

**Purpose:** convert the existing FEVER feasibility plan into an owner decision gate and implementation backlog for a separate academic claim-verification track.  
**Current status:** `DECISION_REQUIRED`; Track B remains disabled and synthetic-only.  
**Scope:** planning and static readiness only. No FEVER data, rows, models, packages, or inference were accessed.

## 1. Decision gate

The owner must decide whether to authorize a **rights-and-suitability assessment of one named FEVER release for an academic-only Track B prototype**. This is narrower than authorizing acquisition, training, model distribution, public hosting, or commercial use.

The official FEVER page and paper establish the claim-verification task, evidence fields, and three labels. The official license notice says the annotations incorporate Wikipedia material and must follow applicable Wikipedia article terms, or CC BY-SA 3.0 where article terms are unavailable. The exact release count is not yet reconciled: the FEVER page states 185,445 claims while the official repository README states 185,441.

Sources:

- [FEVER dataset documentation](https://fever.ai/dataset/fever.html)
- [FEVER license notice](https://fever.ai/download/fever/license.html)
- [FEVER paper](https://aclanthology.org/N18-1074/)
- [FEVER repository](https://github.com/awslabs/fever)

### Owner decision fields — currently undecided

| Decision | Allowed value to record | Current status |
|---|---|---|
| Assess a named FEVER release for academic Track B | Yes / No | `UNDECIDED` |
| Store or display evidence excerpts | Yes / No / Links only | `UNDECIDED` |
| Train or fine-tune a model | Yes / No / Separate approval | `UNDECIDED` |
| Distribute derived data | Yes / No / Legal review | `UNDECIDED` |
| Distribute model weights | Yes / No / Legal review | `UNDECIDED` |
| Host inference publicly | Yes / No / Separate release gate | `UNDECIDED` |
| Commercial use | Yes / No / Legal review | `UNDECIDED` |
| Accountable rights reviewer | Named owner/reviewer | `UNASSIGNED` |

## 2. Activity-by-activity readiness

| Activity | Established by current evidence | Unresolved question | Required evidence or review | Must remain blocked? |
|---|---|---|---|---|
| Local academic experimentation | FEVER defines the labels, claims, evidence references, and a source-conditioned license notice. | Which exact release and Wikipedia-derived material will be used, and whether the planned storage/display fits the applicable terms. | Owner authorization; exact release identity; applicable article terms; attribution/share-alike checklist; qualified rights review if interpretation is needed. | Yes, until the assessment is authorized and the scope is recorded. |
| Training/fine-tuning | The task is suitable for claim-verification research; the official paper describes annotated claims and evidence. | Whether the selected material may be used for training and whether the trained system may be retained or shared. | Written scope decision tied to the exact release; applicable source terms; model/data handling plan; reproducible build and artifact controls. | Yes. |
| Storing/redistributing dataset material | The public page documents JSONL fields and evidence references. | Whether raw claims, evidence text, cached pages, excerpts, or transformed datasets may be stored or redistributed. | Component-level rights review, source-specific terms, attribution/share-alike notices, retention/takedown policy, and owner approval. | Yes. |
| Distributing model weights | No official source reviewed here grants a model-weight distribution right. | Whether weights trained on FEVER-derived material can be distributed under the selected source terms and project policy. | Qualified rights review of the exact training/data pipeline and proposed weight distribution; artifact provenance and trust-root record. | Yes. |
| Public inference demo | FEVER is designed for verification against textual sources, not a public service guarantee. | Evidence source freshness, display rights, privacy, attribution, availability, and whether hosting is permitted. | Separate public-hosting approval, source adapter terms, security/privacy review, monitoring/takedown plan, and model release approval. | Yes. |
| Commercial use | No blanket commercial permission was established. | Whether any applicable source terms permit the intended commercial context. | Qualified legal review or written permission covering the exact activity and material. | Yes. |

Public availability, an academic paper, or the Apache-2.0 license on the FEVER code repository does not resolve the data and source-material questions.

## 3. Implementation boundary

Track B must remain separate from the existing Track A article classifier:

```text
Track A: article text -> Fake/Real model signal
          (existing production boundary; unchanged)

Track B: claim -> permitted evidence source -> evidence validation
          -> SUPPORTED / REFUTED / INSUFFICIENT_EVIDENCE
          (separate, disabled-by-default boundary)
```

The current prototype already provides a useful synthetic contract foundation in:

- `evaluation_results/new_release_candidate_2026-10-22/task44_synthetic_prototype/synthetic_claim_api.py`
- `evaluation_results/new_release_candidate_2026-10-22/task44_synthetic_prototype/test_synthetic_claim_api.py`
- `evaluation_results/new_release_candidate_2026-10-22/task44_synthetic_prototype/UI_MOCKUP.html`
- `evaluation_results/new_release_candidate_2026-10-22/task44_synthetic_prototype/TASK44_SYNTHETIC_API_CONTRACT.md`

Static inspection recorded in the feasibility plan shows that this prototype does not retrieve evidence, load a model, call Wikipedia, expose a production route, or verify real claims.

## 4. Implementation backlog

Engineering estimates are approximate agent working time, not calendar duration. Waiting for owner or legal decisions is separate and unknown.

### B0 — Record the owner scope decision

**Dependency:** none.  
**Can proceed now:** no; requires owner input.  
**Work:** select a named FEVER release for assessment, intended academic scope, evidence storage/display policy, and accountable reviewer.  
**Acceptance criteria:** a written decision record exists; it explicitly does not authorize unlisted uses.  
**Estimate:** 0.5–1 engineering hour to record; external waiting time unknown.

### B1 — Freeze the Track B contract and boundary

**Dependency:** none for synthetic work.  
**Can proceed now:** yes.  
**Work:** document the separate request/response schema, permitted outcomes, source-reference fields, disabled-by-default configuration, and explicit prohibition on Track A conversion.  
**Acceptance criteria:** synthetic tests cover valid requests, all outcomes, malformed payloads, missing evidence, hostile strings, service failure, and production-mode refusal; no Track A route imports Track B.  
**Estimate:** 2–4 agent-hours.

### B2 — Define evidence provenance records

**Dependency:** B0 for the intended source and retention scope.  
**Can proceed now:** schema and synthetic tests can proceed; real-source binding cannot.  
**Work:** define `source_id`, canonical URL or snapshot identifier, page title, sentence/offset reference, retrieval or snapshot timestamp, source version, license notice, excerpt hash, and evidence-status fields.  
**Acceptance criteria:** every displayed evidence item is traceable to a permitted source identity; missing or unverifiable provenance yields `INSUFFICIENT_EVIDENCE`; no fabricated citations appear in fixtures.  
**Estimate:** 3–5 agent-hours.

### B3 — Implement a replaceable evidence-source interface

**Dependency:** B0 and B2.  
**Can proceed now:** interface and synthetic adapter only; FEVER adapter waits for approved data/source access.  
**Work:** define lookup, normalization, source metadata, failure, stale-source, and rate-limit interfaces without connecting to production.  
**Acceptance criteria:** synthetic integration tests cover hit, miss, malformed source, timeout, contradictory evidence, and source-attribution output; no network is required for unit tests.  
**Estimate:** 4–8 agent-hours.

### B4 — Add evidence-aware adjudication and abstention

**Dependency:** B2–B3 and an approved model or deterministic baseline.  
**Can proceed now:** policy and synthetic fixtures can proceed; real adjudication waits for approved artifacts.  
**Work:** distinguish retrieved evidence from model interpretation; require valid evidence for `SUPPORTED`/`REFUTED`; abstain on weak, missing, stale, contradictory, or out-of-scope evidence.  
**Acceptance criteria:** no positive verdict without valid evidence; contradictory evidence never becomes an automatic refutation; uncertainty is presented as a model signal, not factual certainty.  
**Estimate:** 4–8 agent-hours.

### B5 — Build the separate Track B UI

**Dependency:** B1–B4 response schema.  
**Can proceed now:** synthetic UI and error states can proceed.  
**Work:** create a separate claim-verification view with claim input, evidence links/excerpts, source date/version, limitations, loading/error states, and persistent “not an authoritative fact-check” language.  
**Acceptance criteria:** no Fake/Real labels or Track A confidence language appear; malformed evidence is inert; missing evidence and source failure are understandable; recovery is tested.  
**Estimate:** 3–6 agent-hours.

### B6 — Add reproducibility and artifact trust controls

**Dependency:** B0–B4 and a selected model/source.  
**Can proceed now:** requirements and manifest schema can be drafted; real lock/artifact binding waits for approved inputs.  
**Work:** record exact FEVER revision, source snapshot, preprocessing commit, dependency lock, model identity, artifact hashes, configuration, and independent trust-root verification.  
**Acceptance criteria:** clean target environment can be reproduced; artifacts are verified before loading; no same-host unsigned manifest is treated as the trust root.  
**Estimate:** 4–8 agent-hours, excluding dependency acquisition and model training.

### B7 — Evaluate verdict and evidence retrieval separately

**Dependency:** approved release data/source, model, split policy, and reproducible environment.  
**Can proceed now:** evaluation protocol design and synthetic test cases only.  
**Work:** measure verdict metrics, evidence retrieval metrics, abstention coverage, contradiction handling, source/date leakage, and freshness limitations.  
**Acceptance criteria:** exact data/source revision and split manifest are recorded; results are reproducible; benchmark scores are not described as general fact-checking accuracy.  
**Estimate:** 6–12 agent-hours, excluding training and data acquisition.

### B8 — Academic release review

**Dependency:** B0–B7 plus rights and artifact review.  
**Can proceed now:** checklist drafting only.  
**Work:** review attribution, source notices, privacy, takedown, model/data distribution, dependency, security, and owner scope.  
**Acceptance criteria:** owner explicitly approves the exact academic scope; Track A remains unchanged; public hosting is not implied.  
**Estimate:** 2–4 engineering hours, excluding reviewer waiting time.

## 5. Fastest responsible sequence

### Next three tasks

1. **B0 — Owner scope decision.** Required before FEVER-specific assessment or acquisition. This is the immediate blocker.
2. **B1/B2 — Freeze the separate contract and provenance schema.** These can proceed immediately using synthetic fixtures only.
3. **B3/B5 — Build the source-adapter seam and separate UI against synthetic adapters.** These advance the product without FEVER data, network access, or models.

After owner approval and rights review, proceed to B4, B6, B7, and B8 in order. FEVER acquisition and model work remain separate gated steps.

### Revised effort and waiting-time view

| Workstream | Engineering effort | External waiting/approval |
|---|---:|---|
| Owner decision and records | 0.5–1 hour | Owner availability; legal/reviewer availability unknown |
| Synthetic contract, provenance schema, adapter seam, UI | 12–23 hours | None if limited to synthetic fixtures |
| Approved-source integration and adjudication | 8–16 hours | FEVER/source approval and permitted access |
| Reproducible model/artifact/evaluation work | 10–20 hours | Dataset access, model approval, dependency source, rights review |
| Academic release review | 2–4 hours | Owner and qualified reviewer decision |
| **Approximate total after approvals** | **32.5–64 hours** | **Not estimable from current evidence** |

The first safe engineering increment is the synthetic contract/provenance/UI seam. It does not require FEVER acquisition and does not change Track A.

## 6. Conditions that keep the work blocked

Stop and retain `INSUFFICIENT_EVIDENCE` if any of the following is missing:

- exact FEVER release identity and reconciled file/count metadata;
- applicable source/article terms for the material retained or displayed;
- attribution and share-alike handling;
- owner-approved intended-use scope;
- approved evidence source or snapshot;
- trusted model artifact and dependency record;
- evaluation protocol and leakage controls;
- explicit authorization for any public, commercial, model-distribution, or raw-data use.

No synthetic test pass can clear these gates.

## Evidence sources and prior records

This checklist adds decision and sequencing detail to:

- `FEVER_FEASIBILITY_AND_IMPLEMENTATION_PLAN.md`
- `REPLACEMENT_DATASET_ASSESSMENT.md`
- `MODEL_RELEASE_PREREQUISITES.md`
- `evaluation_results/new_release_candidate_2026-10-22/task44_synthetic_prototype/synthetic_claim_api.py`
- `evaluation_results/new_release_candidate_2026-10-22/task44_synthetic_prototype/test_synthetic_claim_api.py`
- `evaluation_results/new_release_candidate_2026-10-22/task44_synthetic_prototype/UI_MOCKUP.html`

The FEVER facts and licensing language are sourced from the official links listed in the feasibility plan. This document distinguishes published facts from proposed engineering controls and unresolved rights questions; it is not legal advice or approval.

## Conclusion

`DECISION_REQUIRED` — prepare the synthetic contract/provenance/UI seam immediately if desired, but wait for the owner's explicit FEVER scope decision before any acquisition, data processing, model work, public hosting, or distribution.
