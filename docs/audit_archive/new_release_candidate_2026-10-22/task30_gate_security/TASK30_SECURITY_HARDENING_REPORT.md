# Task 30 — Evidence Verification and Cross-Gate Security Hardening

## Executive result

**CONDITIONAL PASS for the new strict synthetic verification path; release remains BLOCKED.** The candidate-only preflight now has a strict `run_preflight_secure` entrypoint that recomputes source/evidence-file hashes, enforces policy/configuration binding, validates a concrete partition schema, verifies an externally trusted Ed25519 approval signature, and checks an actual dependency-lock file hash. Synthetic tests pass and the strict path never enables training.

The legacy Task 28 `run_preflight` compatibility path remains structurally weaker because its existing tests and schema predate these trust-boundary changes. It must not be used by a real-data runner; migration to `run_preflight_secure` is required before any runner is considered. No production trust root, owner signature, complete real manifest schema, dataset authorization, or deployment approval exists.

## Task 29 findings reproduced

The original `run_preflight` checked `manifest_sha256` and `certificate_sha256` only with `_sha`, accepted `authenticated: true` as a field, accepted partition-integrity booleans, accepted environment status/approval fields, and made `expected_policy_fingerprint` optional. Task 29 synthetic tests confirmed that editable authenticated claims and unbound manifest/certificate digests could reach the synthetic stopped state.

Those findings remain true for the legacy `task28_evidence_v1` compatibility path. The strict implementation does not rely on those fields as proof.

## Implemented strict protections

`run_preflight_secure` in `candidate_runner_preflight.py` now:

- rehashes local source files as bytes and compares them with a separate `trusted_source_digests` mapping;
- resolves manifest, certificate, environment, lock, and approval paths below a strict evidence root, rejecting absolute paths, traversal, symlinks, and non-files;
- rehashes each evidence file and requires its digest to match an external `trusted_file_digests` mapping;
- requires a supplied expected policy configuration and binds its canonical SHA-256 fingerprint to the selected policy;
- validates manifest schema, exact partition names, row membership, unique/complete expected row IDs, group disjointness, source hashes, policy identity, and mixed-label metadata;
- requires the certificate to bind the exact manifest digest, source hashes, policy ID, and policy fingerprint;
- requires a complete environment lock status, exact Python/platform match, and an actual lock-file digest match;
- verifies Ed25519 approval signatures over a canonical payload binding candidate ID, source hashes, policy ID/fingerprint, manifest/certificate/environment digests, scope, and decision;
- rejects unknown/revoked keys and prohibits `test-*` keys when `test_only=false`;
- keeps `training_permitted=false`, creates no output directory, and performs no model/data processing even after a synthetic strict pass.

The Ed25519 verifier is a standard-library implementation added because no local `cryptography`, PyNaCl, or OpenSSL executable was available. Test keys are generated deterministically inside tests only. They are not stored as project trust roots and cannot be selected in non-test mode.

## Tests run

Task 30 command:

```text
python -m unittest discover -s evaluation_results/new_release_candidate_2026-10-22/task30_gate_security -p "test_*.py" -q
```

Result: **13 passed, 0 failed**.

Covered cases include wrong file bytes, incorrect certificate binding, self-reported unsigned hashes, missing/wrong policy fingerprints, signatures bound to different dataset evidence, modified signed payloads, revoked/untrusted/test keys, incomplete/overlapping/group-crossing manifests, missing membership, environment/lock mismatch, malformed environment, path escape, unsigned records, and synthetic all-gates pass with training still disabled.

Task 29 regression command:

```text
python -m unittest discover -s evaluation_results/new_release_candidate_2026-10-22/task29_gate_integration_audit -p "test_*.py" -q
```

Result: **9 passed, 0 failed**.

Task 28 preflight command:

```text
python -m unittest discover -s evaluation_results/new_release_candidate_2026-10-22/task28_runner_preflight -p "test_*.py" -q
```

Result: **17 passed, 0 failed**.

Existing harness command:

```text
python -m pytest evaluation_results/new_release_candidate_2026-10-22/harness/tests/test_isolated_build_harness.py -q
```

Result: **17 passed, 1 skipped**. The existing privilege-dependent native symlink test remains skipped as documented by Task 24.

## Trust boundary and remaining limitations

The strict verifier proves only that bytes match an externally supplied digest set and that a signature verifies under an externally supplied public key. It does not establish that the key holder is legally authorized, that the dataset license permits intended use, or that the source records are authentic unless the external trust root is independently provisioned.

The existing production manifests are not rewritten or regenerated. Their available records do not establish the Task 30 partition-membership schema, so they remain blocked rather than being treated as validated. The environment gate requires a complete lock in the strict path; the existing Task 25 snapshot therefore cannot pass it.

The legacy `run_preflight` remains present only for compatibility with earlier synthetic tests. A future real-data runner must reject `task28_evidence_v1` and call `run_preflight_secure` with independently provisioned digest and public-key trust roots. This migration is a required next implementation task.

## Safety and scope audit

HEAD before and after: `8c41ae005f4bee178a2b0104cb29049f00182081`. Changes were limited to the candidate-only Task 28 preflight implementation and new Task 30 files. Existing Task 22–29 reports, tests, manifests, datasets, and production files were preserved.

No real dataset rows were processed for training or evaluation. No model artifact was loaded, downloaded, modified, or created. No package was installed and no network was accessed. No real key, signature, approval, license, or release authorization was fabricated. The synthetic test key is not a production trust root.
