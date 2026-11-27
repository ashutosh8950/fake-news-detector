# Task 29 — End-to-End New-Release Gate Integration Audit

## Executive result

**FAIL for end-to-end gate integration security; synthetic refusal behavior is otherwise effective.** The Task 28 preflight reliably refuses many malformed or inconsistent synthetic inputs and never launches training, creates a candidate directory, loads models, or reads dataset rows. However, two gaps prevent a PASS:

1. Manifest and certificate hash fields are only shape-checked; the code does not read the referenced files or prove that the certificate authenticates the exact manifest bytes.
2. `release_authorization.authenticated == true` is accepted from an editable mapping without cryptographic signature verification, trusted-key validation, or binding to the exact dataset, policy, and partition hashes. A fully populated unsigned local record can therefore reach `PREFLIGHT_PASS_STOPPED_BEFORE_TRAINING`.

These gaps leave the real-data release blocked. No source code was changed outside this new Task 29 directory, and no attempt was made to bypass the gates.

## Gate-to-evidence findings

The machine-readable matrix is in `GATE_TO_EVIDENCE_MATRIX.json`. The important distinction is between checks that validate values structurally and checks that establish trust:

- Dataset identity validates repository-relative path syntax, hash shape, matching path/hash sets, and a supplied approval source. It does not hash the actual data files or authenticate the approver.
- Provenance/licensing requires `reviewed`, `approved`, an evidence source, and the three intended-use strings. It does not validate rights-holder authority or legal evidence.
- Grouping policy checks the policy ID and fingerprint format. Exact matching occurs only if the caller supplies `expected_policy_fingerprint`; the function does not require that argument and does not consume the Task 26 approval template.
- Partition evidence checks a derived fingerprint over the supplied dataset hash mapping and policy ID. It does not open the manifest, certificate, or source data. `manifest_sha256` and `certificate_sha256` are not recomputed or mutually bound.
- Partition integrity accepts supplied booleans for disjointness, coverage, and leakage. The underlying manifest is not parsed or independently verified by this module.
- Environment checks accept a reviewed record with `complete` or `accepted_with_limitations`, but do not authenticate the record or compare it with the current interpreter.
- Path containment and report overwrite protection are implemented in `_validate_output_root` and `write_gate_report`. The preflight function itself creates no candidate directory. Native filesystem race and privilege-dependent symlink behavior remain outside proof.
- Release authorization checks four editable fields. There is no signature verifier, trusted-key store, signer identity check, or exact-evidence binding.
- The execution boundary is strong for this module: imports are standard-library only, no training entry point exists, `training_permitted` is always false, and synthetic all-gates pass creates no output directory.

## Cross-gate synthetic testing

The integration tests exercise the actual `run_preflight` implementation:

```text
python -m unittest discover -s evaluation_results/new_release_candidate_2026-10-22/task29_gate_integration_audit -p "test_*.py" -v
```

Result: **9 passed, 0 failed**.

The suite covers source-hash mismatch, policy-fingerprint mismatch, unknown licensing, missing lock acceptance, stale prior results, unsigned authorization, valid-but-unbound certificate/manifest values, editable authenticated claims, and synthetic all-gates pass with no training permission.

The two tests named `test_valid_certificate_hash_does_not_bind_to_manifest_in_current_code` and `test_editable_authenticated_claim_is_not_cryptographically_verified` intentionally document vulnerabilities observed in the current implementation. They pass because they confirm the unsafe behavior; they are not evidence that the behavior is acceptable.

Existing regression commands:

```text
python -m unittest discover -s evaluation_results/new_release_candidate_2026-10-22/task28_runner_preflight -p "test_*.py" -q
```

Result: **17 passed, 0 failed**.

```text
python -m pytest evaluation_results/new_release_candidate_2026-10-22/harness/tests/test_isolated_build_harness.py -q
```

Result: **17 passed, 1 skipped**. The skip is the previously documented privilege-dependent native symlink case.

## Required remediation before any real-data runner

1. Require a trusted, organization-controlled authorization mechanism. Verify a signature or equivalent authenticated attestation against a trust root outside the editable evidence package.
2. Bind that authorization to the candidate ID, source revision, exact dataset hashes, policy fingerprint, manifest hash, certificate hash, environment record, and intended release scope.
3. Resolve manifest and certificate paths from explicit evidence, recompute their hashes, validate their schema, and independently recompute partition coverage/disjointness/leakage checks before accepting them.
4. Make the expected grouping-policy fingerprint mandatory and consume the owner-approved Task 26 record only after authenticating it.
5. Require a verified environment record and explicitly record whether `accepted_with_limitations` is permitted for the intended release; do not treat it as a complete lock.
6. Exercise native symlink/path behavior in an appropriately privileged test environment while retaining the existing synthetic boundary tests.

Dataset provenance/licensing, owner approval, dependency reconstruction, and release signing remain real-world evidence requirements. Creating additional local JSON files cannot resolve them.

## Scope and safety confirmation

HEAD before and after: `8c41ae005f4bee178a2b0104cb29049f00182081`. Existing user changes and untracked files were preserved. New files are confined to `task29_gate_integration_audit/`.

No dataset contents were processed for training or evaluation. No model artifact was loaded, downloaded, modified, or generated. No production code, prior report, existing manifest, or approval record was modified. No real approval, signature, license, or release authorization was fabricated.
