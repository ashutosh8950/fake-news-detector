# Task 42 — Alternative Dataset Rights and Suitability Comparison

## Executive result

No candidate is approved for acquisition, training, model distribution, or public hosting. The strongest academic research lead is **FEVER**, but it is a claim-verification benchmark rather than an article-level fake-versus-real dataset. The strongest article-level leads, **NELA-GT** and the Zenodo v1.1 candidate, retain rights or scope gaps. The existing local dataset remains NO-GO.

## Candidate summary

| Candidate | Technical relationship to TruthScan | Rights evidence | Status |
|---|---|---|---|
| FEVER | 185,445 claims; `SUPPORTS`, `REFUTES`, `NOT ENOUGH INFO`; evidence-based verification, not news-article fake/real | Official license notice binds annotations to applicable Wikipedia terms or CC BY-SA 3.0 where terms are unavailable | `RESEARCH_LEAD` for a separately scoped academic claim-verification demo; public website blocked |
| NELA-GT 2020–2022 | Article-level news collection with outlet-level reliability labels; labels are not direct article truth labels | Official repository describes copyright-aware text transformation but does not establish a broad downstream license | `RESEARCH_LEAD` for permission-dependent research; public website blocked |
| Zenodo 18135595 v1.1 | Record describes labeled fake/disinformation versus true news articles; exact schema not inspected | Record displays CC BY 4.0 for datasets, but underlying article rights and downstream scope are unresolved | `BLOCKED_INSUFFICIENT_EVIDENCE` |
| LIAR | Short political claims with six labels; not article-level binary | Official archive/paper identify source, but downstream license and rights remain unresolved | `BLOCKED_INSUFFICIENT_EVIDENCE` |
| WELFake | Article-level fake-news research lead; exact version/schema and provenance need verification | Official Zenodo record was not retrievable in this audit; no sufficient primary-source license evidence established | `BLOCKED_INSUFFICIENT_EVIDENCE` |

## FEVER

The official FEVER site says the dataset contains 185,445 claims generated from Wikipedia sentences and labels them `SUPPORTS`, `REFUTES`, or `NOT ENOUGH INFO`; evidence links are part of the format. Its official license page says annotations incorporate Wikipedia material and must follow the applicable Wikipedia article terms or CC BY-SA 3.0 when no terms are available. This is materially better documented than candidates with no license notice, but it is not permission to treat claims as fake/real news labels, nor a blanket grant for public model hosting or model distribution.

Technical consequence: TruthScan would need a new claim-verification task, label contract, evidence-aware preprocessing, and separate evaluation. It must not relabel `REFUTES` as “fake” without owner and methodological approval.

## NELA-GT

The official repository documents large article collections, source and date fields, embedded tweets, and outlet-level labels such as reliable, unreliable, and mixed. It explicitly says source articles may be copyrighted and applies a text transformation intended to prevent ordinary news consumption while retaining analysis utility. That is evidence of a copyright-aware design, not a general license or permission for public hosting, commercial use, model distribution, or raw-data redistribution.

Technical consequence: the source-level labels are vulnerable to outlet/source shortcuts and do not directly establish article-level truth. A new grouping policy by outlet and article identity would be essential.

## Zenodo v1.1, LIAR, and WELFake

These remain leads only. Task 40 found a record-level CC BY assertion for Zenodo but no verified underlying-content rights. Task 38 found LIAR’s source and task description but no downstream license. WELFake’s exact primary record/license was not verified in this read-only pass. None is approved.

## Track decisions

### College demonstration

Status: `BLOCKED_INSUFFICIENT_EVIDENCE` for a TruthScan fake/real model. FEVER may be considered as a separately named academic fact-verification demonstration after owner authorization and review of applicable Wikipedia terms. That would not be the existing TruthScan task and would not authorize public hosting.

### Public website

Status: `BLOCKED_INSUFFICIENT_EVIDENCE` for every candidate. No reviewed candidate supplies a complete, independently verified basis covering public inference hosting, commercial status, model artifacts, privacy/takedown, and third-party content.

No dataset was downloaded or parsed. Suitability claims are based on published metadata only.

## Sources reviewed on 2026-10-22

- FEVER dataset: https://fever.ai/dataset/fever.html
- FEVER license: https://fever.ai/download/fever/license.html
- FEVER official repository: https://github.com/awslabs/fever
- NELA-GT official repository: https://github.com/MELALab/nela-gt
- Zenodo v1.1: https://zenodo.org/records/18135595
- LIAR official archive: https://sites.cs.ucsb.edu/~william/data/
- LIAR paper: https://arxiv.org/abs/1705.00648
- WELFake record lead: https://zenodo.org/records/4561253

Public source availability and a displayed license were not treated as proof of complete rights in third-party content.
