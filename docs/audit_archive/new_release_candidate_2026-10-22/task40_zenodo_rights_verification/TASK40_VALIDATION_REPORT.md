# Task 40 — Validation Report

## Result

**CONDITIONAL PASS for read-only rights verification; both intended-use gates remain blocked.**

## Sources checked

- Zenodo record: https://zenodo.org/records/18135595 — accessible; reviewed 2026-10-22.
- Creative Commons official CC BY 4.0 deed: https://creativecommons.org/licenses/by/4.0/ — accessible; reviewed 2026-10-22.
- Zenodo metadata API: https://zenodo.org/api/records/18135595 — inaccessible through the read-only source interface; not treated as evidence of absence.
- Zenodo linked working-paper target — returned a cache-miss/inaccessible result; not treated as evidence of absence.

## Validation checks

- All four JSON files parse successfully using Python’s standard JSON parser.
- Required status fields are present and both gates are `BLOCKED_INSUFFICIENT_EVIDENCE`.
- Both gates have `refusal_default: true`, owner decision `PENDING`, and all authorization booleans false.
- The evidence register records accessible and inaccessible sources separately.
- The report distinguishes record-level CC BY facts from unresolved underlying-content rights.
- No candidate is marked approved, release-ready, or authorized.

## Safety and scope

No dataset files were downloaded, no dataset rows were retrieved or processed, and no model was loaded, trained, evaluated, or generated. No production code, data, secure preflight, trust roots, release gates, or prior reports were modified. No rights holder or author was contacted.

## Git state

Initial and final HEAD: `8c41ae005f4bee178a2b0104cb29049f00182081`.

Pre-existing modifications and untracked files were preserved. New work is confined to this Task 40 directory.

## Limitations

The dataset ZIP contents were intentionally not downloaded or inspected. Consequently, exact schema, labels, article sources, duplicate structure, and transformations remain unverified. This is not legal advice and does not establish that Zenodo’s record creator had authority over every third-party work.
