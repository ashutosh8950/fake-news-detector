# Task 39 — Dual-Track Dataset Selection Recommendation

## Executive recommendation

**No candidate is selected or authorized.** The strongest evidence-supported conclusion is to keep both the college-demo and public-website tracks blocked pending an owner decision, rights review, and a separately authorized acquisition workflow.

The Zenodo record `10.5281/zenodo.18135595` is the strongest new *research lead*: it identifies a versioned package, creator, DOI, article-level fake/true datasets, and a CC BY 4.0 label for the dataset package. That record does not establish that all underlying news text and third-party material are licensed for every downstream use, and it does not expressly grant public inference hosting, model-artifact distribution, or raw-data redistribution rights. It is not approved for acquisition.

LIAR remains a useful claim-level research lead but is not a direct replacement for TruthScan’s article-level binary task. Fakeddit, CoAID, and FakeNewsNet require materially different task and rights reviews; FakeNewsNet’s official documentation expressly restricts complete redistribution.

## Existing dataset status

The local `Fake.csv`/`True.csv` corpus remains **NO-GO / `BLOCKED_INSUFFICIENT_EVIDENCE`**. Tasks 36–38 did not recover an authenticated acquisition chain, source-to-local mapping, source digest, transformation receipt, license snapshot, or rights-holder permission. Local hashes establish consistency with local records only.

## Candidate comparison

| Candidate | Technical fit | Evidence-supported rights conclusion | Main blocker |
|---|---|---|---|
| Zenodo record 18135595 v1.1 | Closest apparent article-level fake/true structure; exact schema and contents require review after authorization | `CONDITIONAL_PENDING_CONFIRMATION` for research consideration; public-track uses `BLOCKED_INSUFFICIENT_EVIDENCE` | Underlying article/third-party rights, exact file identity, downstream-use permissions |
| LIAR | Claim-level, six labels; not a drop-in binary article corpus | Research `CONDITIONAL_PENDING_CONFIRMATION`; downstream uses blocked | PolitiFact/source rights and no verified downstream license |
| Fakeddit | Reddit-derived multimodal/text components; not direct binary article replacement | Research `CONDITIONAL_PENDING_CONFIRMATION`; downstream uses blocked | Reddit/user/media rights, deletion/privacy, dataset-specific license |
| CoAID | COVID-health misinformation domain; different task contract | Research `CONDITIONAL_PENDING_CONFIRMATION`; downstream uses blocked | Rights, domain mismatch, social/article content |
| FakeNewsNet | News/social provenance lead; not a direct corpus replacement | Research permission-dependent; raw redistribution `PROHIBITED_BY_DOCUMENTED_TERMS` | Official README says complete dataset cannot be distributed |

Published metadata does not justify an accuracy or performance ranking. No dataset was downloaded or parsed.

## Track A — College demonstration

Status: **`BLOCKED_INSUFFICIENT_EVIDENCE`**; acquisition, training, artifact creation, and deployment are **not authorized**.

Before a demonstration can proceed, the owner must select a candidate and authorize research-only rights verification, then establish the exact version/file digests, source-to-local acquisition record, applicable license/permission, intended academic use, attribution obligations, grouping and leakage policy, reproducible environment, and an approved non-production build. The demo must disclose that outputs are research demonstrations and not authoritative fact-checking.

Academic context does not automatically grant permission to copy, process, redistribute, or publicly host the data or model.

## Track B — Public website

Status: **`BLOCKED_INSUFFICIENT_EVIDENCE`**; public hosting, commercial use, model distribution, training, artifact creation, and deployment are **not authorized**.

This track additionally requires rights reviewed for public inference hosting and the intended commercial/non-commercial status, model-artifact handling, third-party content and privacy/takedown obligations, dependency and artifact integrity, monitoring, security review, and explicit release/deployment approval. A dataset package license alone is not treated as a hosting or model-distribution grant.

## Recommended next action

Ask the owner to authorize **research-only comparison and rights verification** for either the Zenodo candidate, one earlier candidate, or both. Do not acquire any candidate until the owner records intended uses and responsible rights approver. If Zenodo is selected, the next intake must obtain the exact versioned file inventory and digests, review the attached CC BY 4.0 terms and third-party-content scope, and obtain qualified confirmation for public hosting/model distribution. No build should start before all existing preflight gates pass.

## Sources and limits

- Zenodo record, v1.1 published 2026-01-02: https://zenodo.org/records/18135595
- LIAR paper: https://arxiv.org/abs/1705.00648
- LIAR official UCSB archive: https://sites.cs.ucsb.edu/~william/data/
- Fakeddit official repository: https://github.com/entitize/Fakeddit
- Fakeddit paper: https://arxiv.org/abs/1911.03854
- Reddit Public Content Policy, updated 2026-10-06: https://support.reddithelp.com/hc/en-us/articles/26410290525844-Public-Content-Policy
- CoAID official repository: https://github.com/cuilimeng/CoAID
- FakeNewsNet official repository: https://github.com/KaiDMML/FakeNewsNet
- PolitiFact terms relevant to LIAR-origin material: https://politifact.com/copyright/

Sources were reviewed read-only on 2026-10-22. The record of a license or public hosting page is evidence of what the publisher states, not proof of every underlying contributor’s authority or of the legality of each proposed use.
