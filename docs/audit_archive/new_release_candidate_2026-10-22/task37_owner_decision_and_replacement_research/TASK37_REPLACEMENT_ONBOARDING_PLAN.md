# Task 37 — Replacement-Dataset Onboarding Plan

This is a proposed fail-closed process. None of these steps was executed in
Task 37.

1. Obtain explicit project-owner authorization to research one named candidate.
2. Define the intended uses before acquisition: internal evaluation, model
   artifact distribution, public hosting, commercial use, and raw-data
   redistribution.
3. Review the official license or written permission for the exact revision.
   Confirm that the person or organization granting permission has authority.
4. Resolve third-party rights for article text, headlines, images, comments,
   social identifiers, metadata, and linked publisher content.
5. In a separately authorized acquisition, record source URL, exact revision,
   acquisition method/date, source artifact digest, local digest, file sizes,
   schema, and transformation receipts. Preserve the original evidence without
   relying on a mutable download URL alone.
6. Obtain owner/legal sign-off on the selected intended-use scope and all
   attribution, noncommercial, share-alike, privacy, takedown, and retention
   obligations.
7. Define the new task contract: labels, schema, preprocessing, candidate
   output format, and known domain limitations. Do not assume compatibility with
   `Fake.csv`/`True.csv`.
8. Approve a grouping policy and leakage-resistant train, selection,
   calibration, and test partitions for the exact acquired revision.
9. Establish an exact dependency lock and language-model/package integrity
   record. Keep the environment gate separate from dataset rights.
10. Provision trust roots independently, bind approvals to exact source and
    partition digests, and run the existing secure preflight without weakening
    it.
11. Obtain explicit authorization before any real-data training, calibration,
    evaluation, or artifact generation. Keep the build isolated from production
    paths.
12. Perform separate compatibility, release-authentication, deployment,
    hosting, rollback, and audit-retention reviews before distribution or public
    service activation.

At every stage, missing, stale, unsigned, mismatched, or self-asserted evidence
must stop the process. A new candidate may establish provenance for a new
release; it cannot establish historical authenticity or equivalence.
