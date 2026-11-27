"""Deterministic, hand-authored Track B demonstration.

This runner demonstrates contract flow only. It does not retrieve evidence,
call a model, read a dataset, or make a factual claim about the world.
"""

from __future__ import annotations

import json
from typing import Any

from synthetic_claim_api import OUTCOMES, validate_response


SYNTHETIC_DEMO_EXAMPLES = (
    {
        "example_id": "synthetic-supported-1",
        "synthetic": True,
        "claim": "A synthetic fixture says the sample sky is blue.",
        "assigned_outcome": "SUPPORTED",
        "evidence_rationale": "The hand-authored fixture evidence is written to support this assigned outcome.",
        "response": {
            "track": "claim_verifier",
            "task": "fever_claim_verification",
            "outcome": "SUPPORTED",
            "score": 1.0,
            "evidence": [{
                "source_id": "SYNTHETIC-ONLY-SOURCE-1",
                "title": "Synthetic evidence card 1",
                "snippet": "Synthetic fixture evidence: the sample sky is blue.",
                "source_url": "synthetic://fixture/source-1",
                "source_version": "synthetic-v1",
                "retrieved_at": "synthetic-time",
            }],
            "limitations": ["Hand-authored synthetic example; no real source was checked."],
            "disclaimer": "Synthetic demonstration only; not an authoritative fact-check.",
        },
    },
    {
        "example_id": "synthetic-refuted-1",
        "synthetic": True,
        "claim": "A synthetic fixture says the sample stone floats in water.",
        "assigned_outcome": "REFUTED",
        "evidence_rationale": "The hand-authored fixture evidence is written to refute this assigned outcome.",
        "response": {
            "track": "claim_verifier",
            "task": "fever_claim_verification",
            "outcome": "REFUTED",
            "score": 1.0,
            "evidence": [{
                "source_id": "SYNTHETIC-ONLY-SOURCE-2",
                "title": "Synthetic evidence card 2",
                "snippet": "Synthetic fixture evidence: the sample stone sinks in water.",
                "source_url": "synthetic://fixture/source-2",
                "source_version": "synthetic-v1",
                "retrieved_at": "synthetic-time",
            }],
            "limitations": ["Hand-authored synthetic example; no real source was checked."],
            "disclaimer": "Synthetic demonstration only; not an authoritative fact-check.",
        },
    },
    {
        "example_id": "synthetic-insufficient-1",
        "synthetic": True,
        "claim": "A synthetic fixture makes an unsupported statement.",
        "assigned_outcome": "INSUFFICIENT_EVIDENCE",
        "evidence_rationale": "No synthetic evidence card is supplied, so the contract abstains.",
        "response": {
            "track": "claim_verifier",
            "task": "fever_claim_verification",
            "outcome": "INSUFFICIENT_EVIDENCE",
            "score": 0.0,
            "evidence": [],
            "limitations": ["No evidence supplied; this is a synthetic abstention example."],
            "disclaimer": "Synthetic demonstration only; not an authoritative fact-check.",
        },
    },
)


def build_demo_results() -> list[dict[str, Any]]:
    """Validate and return the three hand-authored synthetic examples."""
    results = []
    for example in SYNTHETIC_DEMO_EXAMPLES:
        if example["synthetic"] is not True:
            raise ValueError("Every demonstration example must be marked synthetic")
        assigned = example["assigned_outcome"]
        if assigned not in OUTCOMES:
            raise ValueError("Demonstration uses an unsupported outcome")
        validated = validate_response(example["response"])
        if validated["outcome"] != assigned:
            raise ValueError("Assigned outcome does not match validated response")
        results.append({
            "example_id": example["example_id"],
            "synthetic": True,
            "claim": example["claim"],
            "assigned_outcome": assigned,
            "evidence_rationale": example["evidence_rationale"],
            "response": validated,
        })
    return results


def main() -> None:
    print(json.dumps({
        "demo": "TruthScan Track B synthetic evidence-to-verdict demonstration",
        "synthetic_only": True,
        "results": build_demo_results(),
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
