# Task 40 — Zenodo v1.1 Rights Verification Report

## Executive decision

**College demonstration: `BLOCKED_INSUFFICIENT_EVIDENCE`.**

**Public TruthScan website: `BLOCKED_INSUFFICIENT_EVIDENCE`.**

The Zenodo record is a useful, identifiable research lead, not an approved acquisition or release source. It verifies a v1.1 record published January 2, 2026, creator Sadam Hussain of Goldsmiths University of London, DOI `10.5281/zenodo.18135595`, two named ZIP assets, and a displayed CC BY 4.0 label for the datasets. It does not establish a complete rights chain for the underlying news articles, nor expressly grant public inference hosting, commercial use, model-artifact distribution, or raw-data redistribution for TruthScan.

No dataset file or row was downloaded or inspected. The exact dataset schema, labels, article sources, duplicate structure, and transformations therefore remain unverified.

## Verified record metadata

Source: [Zenodo record 18135595](https://zenodo.org/records/18135595), reviewed read-only on 2026-10-22.

- Title: “Disinformation Detection: Code and Datasets v1.1”.
- Version/publication: v1.1; published January 2, 2026.
- Creator: Sadam Hussain; affiliation shown as Goldsmiths University of London.
- DOI: `10.5281/zenodo.18135595`.
- Description: code and datasets for disinformation-detection research.
- Dataset asset name: `disinformation:Fake_detection_datasets_v1.1.zip`.
- Dataset asset display: 327.2 MB; MD5 displayed as `64b4e8888f95ec104611de9d01ffe903`.
- Code asset name: `Disinformation:Fake News Detection Code v1.1.zip`.
- Code asset display: 41.3 kB; MD5 displayed as `471a3e4d0a227b58c2500cd2cee5e8df`.
- Stated dataset license: Creative Commons Attribution 4.0 International (CC BY 4.0).
- Record describes labeled news articles as disinformation/fake news versus true news and mentions multilingual content, but does not provide enough metadata to verify the exact label schema or source rights without opening the files.

The displayed MD5 values are useful record metadata for a future controlled acquisition. They are not an independently authenticated source-to-local mapping and were not compared with local files.

## What CC BY 4.0 establishes and does not establish

The [official Creative Commons deed](https://creativecommons.org/licenses/by/4.0/) states that licensed material may be shared and adapted, including commercially, subject to attribution and no-additional-restrictions requirements. It also states that a license may not provide all permissions needed for an intended use, including privacy, publicity, or moral-rights permissions, and that the deed itself is only a summary.

Accordingly, the Zenodo label supports only this narrower conclusion: the record publisher presents the dataset package as CC BY 4.0. It does not prove that the publisher owns or may relicense every article, image, metadata field, author identity, or other third-party element included in the package. It also does not, without further analysis, answer whether a trained model or a public inference service is permitted under the rights of those underlying elements.

## Provenance and underlying-content review

The record identifies the creator and package version, but the reviewed metadata does not identify:

- the original publishers or URLs for each article;
- an acquisition date, collection method, or source revision for each article;
- permissions or licenses from news publishers or authors;
- transformations, filtering, deduplication, or relabeling receipts;
- a signed or independently authenticated provenance statement;
- deletion, correction, takedown, privacy, or retention handling;
- an explicit grant for public hosting, model distribution, or commercial deployment.

The linked working-paper target was not independently retrievable through the read-only source interface during this audit. That is recorded as an access limitation, not evidence that no paper or additional terms exist.

## Intended-use decisions

| Activity | Status | Basis |
|---|---|---|
| College/academic demonstration | `BLOCKED_INSUFFICIENT_EVIDENCE` | Record and CC BY label support a research lead, but underlying-content rights, exact file identity, attribution implementation, and intended-use scope are unresolved. |
| Internal research/training | `CONDITIONAL_PENDING_CONFIRMATION` | The record describes research datasets and labels, but permission for the exact underlying content and planned processing is not independently established. |
| Public inference hosting | `BLOCKED_INSUFFICIENT_EVIDENCE` | No explicit hosting grant, third-party rights review, privacy/takedown plan, or owner deployment approval. |
| Commercial use | `BLOCKED_INSUFFICIENT_EVIDENCE` | CC BY is commercially permissive for material actually licensed, but record-level coverage of third-party content and intended service scope is unresolved. |
| Trained-model distribution | `BLOCKED_INSUFFICIENT_EVIDENCE` | No explicit model-distribution permission and no analysis of rights in underlying articles and derived representations. |
| Raw dataset redistribution | `BLOCKED_INSUFFICIENT_EVIDENCE` | Dataset label suggests sharing of licensed material, but exact package scope and third-party rights are not established for redistribution. |

No status is marked `SUPPORTED_BY_VERIFIED_EVIDENCE` or `PROHIBITED_BY_DOCUMENTED_TERMS` for the Zenodo package as a whole. The correct result is an evidence gap, not an assumed permission.

## Technical suitability without data access

The record’s description is directionally compatible with TruthScan’s fake-versus-true news objective, but this is not sufficient for substitution. Before any authorized acquisition, the project must verify the exact binary label definition, class names and order, language and topic coverage, article fields, source/publisher fields, duplicate keys, temporal coverage, and any multilingual preprocessing requirements. Group-aware partitioning must be designed for the actual source and article identities. No performance or equivalence claim is made.

## Reproducible acquisition readiness

The DOI, v1.1 version, named ZIP assets, displayed sizes, and displayed MD5 values provide a reasonable starting identity record. They do not yet constitute a complete reproducible acquisition receipt. A future authorized acquisition must preserve the exact record URL/DOI, retrieval date, asset bytes, cryptographic digest calculated after download, source-reported metadata, license snapshot, transformation commands, and any source-to-content rights evidence. No acquisition was authorized or performed here.

## Required next evidence

1. Owner selects whether Zenodo rights verification should continue and specifies college-only, public non-commercial, commercial, model-distribution, and raw-data uses.
2. A qualified reviewer obtains the exact CC BY 4.0 legal text and assesses what material the record’s license covers.
3. The creator or an authorized rights holder provides a provenance and rights statement covering the included article content and transformations, or identifies exclusions and separate licenses.
4. The project records privacy, takedown, attribution, notice, and third-party-content handling.
5. Only after explicit acquisition authorization, the exact asset bytes and hashes are recorded and the dataset is inspected under the existing secure gates.
6. The owner separately approves any training, artifact release, public hosting, and deployment.

## Safety and repository status

No dataset files were downloaded, no rows were processed, and no model was loaded, trained, evaluated, or generated. No production code, dataset, secure preflight, trust root, release gate, or prior report was modified. No rights holder was contacted.

Initial and final HEAD: `8c41ae005f4bee178a2b0104cb29049f00182081`.

Existing user modifications and untracked files were preserved.
