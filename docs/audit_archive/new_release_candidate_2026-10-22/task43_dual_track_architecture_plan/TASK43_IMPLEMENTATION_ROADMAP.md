# Task 43 — Implementation Roadmap

## Phase 0 — Safe now, no data required

1. Freeze and document Track A baseline contracts and disclaimers.
2. Add synthetic-only schemas and contract tests for separate article and claim routes; do not connect them to model loading.
3. Produce UI mockups that visibly distinguish Fake/Real from Supported/Refuted/Insufficient Evidence.
4. Add architecture/threat-model documentation and route-level authorization checks that default Track B to disabled.
5. Define separate observability fields: track, task, model version, evidence availability, and readiness state.

Acceptance: imports and synthetic requests create no artifacts, load no real models, and never map claim outcomes to Fake/Real.

## Phase 1 — Owner and rights gates

1. Obtain explicit owner decision for FEVER research-only use.
2. Have a qualified reviewer assess the applicable Wikipedia terms and intended academic/public uses.
3. Record exact data/version/source identity only through an authorized acquisition process.
4. Keep public hosting blocked unless separately cleared.

Acceptance: evidence register binds the intended use, source/version, license scope, and decision-maker; missing evidence fails closed.

## Phase 2 — Isolated academic prototype, if authorized

1. Use a separate Track B namespace and approved FEVER schema.
2. Define evidence-aware grouping and train/selection/calibration/test partitions.
3. Produce a separate evaluation protocol for claim verification.
4. Validate the `INSUFFICIENT_EVIDENCE` behavior and evidence-display contract.

Acceptance: functional results are reported only as claim-verification metrics and never as TruthScan fake-news performance.

## Phase 3 — Public website review

Only after rights, reproducibility, security, privacy/takedown, model release, monitoring, and deployment approvals are complete should public hosting be considered. A strong academic benchmark result is not sufficient evidence of public reliability.

## Dependencies and stop conditions

No phase may acquire data, train, or create artifacts while its preceding rights and authorization gates are unresolved. Track B must not share Track A artifacts, metrics, preprocessing, or labels merely for convenience.
