# Candidate Build Workflow

The proposed workflow is a refusal-first boundary. No real build is authorized by this document.

```mermaid
flowchart TD
    Start[Future candidate request]
    Config[Explicit candidate identity and configuration]
    Roots[Independent trusted digest roots and public-key roots]
    Evidence[Dataset, provenance, license, grouping, partition, environment and lock evidence]
    Preflight[Secure preflight and cross-gate binding]
    Check{All required gates valid?}
    Refuse[Refuse; no training, loading or artifacts]
    Disabled[Current state: training_permitted=false\nbuild_authorized=false]
    Owner[Separate owner/release approval]
    Build[Only after authorization: isolated future build]
    Validate[Separate validation and artifact verification]

    Start --> Config --> Roots --> Evidence --> Preflight --> Check
    Check -- no --> Refuse
    Check -- yes --> Disabled
    Disabled --> Owner --> Build --> Validate
```

## Required evidence

The future candidate path must bind the candidate release ID to exact dataset byte digests, provenance/licensing evidence, the approved grouping fingerprint, partition manifest and certificate hashes, dependency-lock/environment records, and an authenticated approval. Trust roots must be provisioned independently of the evidence being verified. Missing, malformed, unsigned, stale, mismatched, or owner-unapproved evidence must refuse.

## Current status

The repository has candidate-only preflight/harness work and synthetic tests, but no real candidate bundle or production trust root. The Task 33–34 orchestration work is architectural/candidate-only and does not override unresolved real-world gates. A synthetic all-gates-passing fixture must still terminate without invoking training.

## Explicit non-claims

This workflow does not authenticate the historical bundle, establish dataset rights, create a lockfile, authorize training, create artifacts, or approve deployment.
