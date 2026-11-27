# Task 44 — Synthetic API Contract

This isolated prototype is not registered with FastAPI and is not imported by the live application.

Request fields are exactly `claim` and `evidence_mode` (`required` or `optional`). Claims must be non-empty and at most 4,000 characters. Unexpected fields are rejected.

Response fields are exactly `track`, `task`, `outcome`, `score`, `evidence`, `limitations`, and `disclaimer`. Outcomes are exactly `SUPPORTED`, `REFUTED`, or `INSUFFICIENT_EVIDENCE`. Each evidence item is an object containing required non-empty bounded `source_id` and `snippet` strings. Optional non-empty bounded metadata fields are `title`, `source_url`, `source_version`, and `retrieved_at`; these fields identify provenance metadata but do not prove that a source is real or permitted. `SUPPORTED` and `REFUTED` require at least one valid evidence item; `INSUFFICIENT_EVIDENCE` must have none.

The fixtures use `SYNTHETIC-ONLY-*` placeholders. They are not citations, sources, or factual conclusions. There is no retriever, model, dataset reader, or network client.
