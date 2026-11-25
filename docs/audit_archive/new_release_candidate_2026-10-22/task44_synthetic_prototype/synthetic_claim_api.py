"""Synthetic-only Track B contract prototype.

This module intentionally has no FastAPI registration, model loading, network
access, filesystem access, or evidence retrieval. It is not production code.
"""

from __future__ import annotations

from html import escape
from typing import Any, Mapping

OUTCOMES = frozenset({"SUPPORTED", "REFUTED", "INSUFFICIENT_EVIDENCE"})
REQUEST_FIELDS = frozenset({"claim", "evidence_mode"})
RESPONSE_FIELDS = frozenset({
    "track", "task", "outcome", "score", "evidence", "limitations", "disclaimer"
})
EVIDENCE_FIELDS = frozenset({
    "source_id", "title", "snippet", "source_url", "source_version", "retrieved_at"
})
REQUIRED_EVIDENCE_FIELDS = frozenset({"source_id", "snippet"})
MAX_CLAIM_LENGTH = 4000
MAX_SOURCE_ID_LENGTH = 200
MAX_TITLE_LENGTH = 300
MAX_SNIPPET_LENGTH = 2000
MAX_SOURCE_URL_LENGTH = 2048
MAX_SOURCE_VERSION_LENGTH = 200
MAX_RETRIEVED_AT_LENGTH = 100


class ContractError(ValueError):
    """Safe, user-facing contract failure without internal details."""


def validate_request(payload: Mapping[str, Any]) -> dict[str, str]:
    if not isinstance(payload, Mapping) or set(payload) != REQUEST_FIELDS:
        raise ContractError("Invalid claim-verification request")
    claim = payload.get("claim")
    mode = payload.get("evidence_mode")
    if not isinstance(claim, str) or not claim.strip() or len(claim.strip()) > MAX_CLAIM_LENGTH:
        raise ContractError("Claim is empty or exceeds the allowed length")
    if mode not in {"required", "optional"}:
        raise ContractError("Invalid evidence mode")
    return {"claim": claim.strip(), "evidence_mode": mode}


def validate_response(payload: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, Mapping) or set(payload) != RESPONSE_FIELDS:
        raise ContractError("Invalid claim-verification response")
    if payload["track"] != "claim_verifier" or payload["task"] != "fever_claim_verification":
        raise ContractError("Invalid claim-verification identity")
    if payload["outcome"] not in OUTCOMES:
        raise ContractError("Unknown claim-verification outcome")
    if isinstance(payload["score"], bool) or not isinstance(payload["score"], (int, float)) or not 0 <= payload["score"] <= 1:
        raise ContractError("Invalid claim-verification score")
    if not isinstance(payload["evidence"], list) or not isinstance(payload["limitations"], list):
        raise ContractError("Invalid claim-verification evidence fields")
    for limitation in payload["limitations"]:
        if not isinstance(limitation, str) or not limitation.strip() or len(limitation) > MAX_SNIPPET_LENGTH:
            raise ContractError("Invalid claim-verification limitation")
    if not isinstance(payload["disclaimer"], str) or not payload["disclaimer"]:
        raise ContractError("Missing claim-verification disclaimer")
    validated_evidence = []
    for item in payload["evidence"]:
        if not isinstance(item, Mapping) or not set(item).issubset(EVIDENCE_FIELDS):
            raise ContractError("Invalid claim-verification evidence item")
        if not REQUIRED_EVIDENCE_FIELDS.issubset(item):
            raise ContractError("Evidence source reference is missing")
        snippet = item.get("snippet")
        if not isinstance(snippet, str) or not snippet.strip() or len(snippet) > MAX_SNIPPET_LENGTH:
            raise ContractError("Evidence text is missing or invalid")
        for field, limit in (
            ("source_id", MAX_SOURCE_ID_LENGTH),
            ("title", MAX_TITLE_LENGTH),
            ("source_url", MAX_SOURCE_URL_LENGTH),
            ("source_version", MAX_SOURCE_VERSION_LENGTH),
            ("retrieved_at", MAX_RETRIEVED_AT_LENGTH),
        ):
            if field in item and (not isinstance(item[field], str) or not item[field].strip() or len(item[field]) > limit):
                raise ContractError("Invalid claim-verification evidence metadata")
        validated_evidence.append(dict(item))
    if payload["outcome"] in {"SUPPORTED", "REFUTED"} and not validated_evidence:
        raise ContractError("This outcome requires supporting evidence")
    if payload["outcome"] == "INSUFFICIENT_EVIDENCE" and validated_evidence:
        raise ContractError("Insufficient-evidence response cannot cite supporting evidence")
    result = dict(payload)
    result["evidence"] = validated_evidence
    return result


def run_synthetic_fixture(payload: Mapping[str, Any], *, environment: str = "test", synthetic_mode: bool = False) -> dict[str, Any]:
    """Return a pre-authored fixture outcome; never predicts or retrieves evidence."""
    if environment == "production" or not synthetic_mode:
        raise ContractError("Track B prototype is disabled")
    request = validate_request(payload)
    fixture = str(request["claim"]).lower()
    if fixture.startswith("synthetic supported"):
        outcome, score, evidence = "SUPPORTED", 0.91, [{"source_id": "SYNTHETIC-ONLY-1", "title": "Synthetic evidence placeholder", "snippet": "Synthetic fixture; not a real source."}]
    elif fixture.startswith("synthetic refuted"):
        outcome, score, evidence = "REFUTED", 0.88, [{"source_id": "SYNTHETIC-ONLY-2", "title": "Synthetic evidence placeholder", "snippet": "Synthetic fixture; not a real source."}]
    else:
        outcome, score, evidence = "INSUFFICIENT_EVIDENCE", 0.0, []
    return validate_response({
        "track": "claim_verifier",
        "task": "fever_claim_verification",
        "outcome": outcome,
        "score": score,
        "evidence": evidence,
        "limitations": ["Synthetic fixture only; no real claim or source was checked."],
        "disclaimer": "Demonstration contract only; not an authoritative fact-check.",
    })


def forbid_track_a_conversion(outcome: str) -> None:
    if outcome in OUTCOMES:
        raise ContractError("Claim-verification outcomes cannot be converted to Fake or Real")


def render_mock_ui(response: Mapping[str, Any]) -> str:
    try:
        result = validate_response(response)
    except ContractError:
        return (
            "<section data-track='claim-verifier' data-state='error'>"
            "<h1>Unable to display result</h1>"
            "<p>Invalid claim-verification response.</p>"
            "</section>"
        )
    evidence = "".join(
        "<li><strong>SYNTHETIC EVIDENCE</strong> — "
        f"{escape(item.get('source_id', 'synthetic-fixture'))}: "
        f"{escape(item.get('title', 'Synthetic placeholder'))} — "
        f"{escape(item['snippet'])}</li>"
        for item in result["evidence"]
    ) or "<li>No evidence available</li>"
    return (
        "<section data-track='claim-verifier'>"
        f"<h1>{escape(result['outcome'])}</h1>"
        f"<p>{escape(result['disclaimer'])}</p>"
        f"<ul>{evidence}</ul>"
        f"<p>{escape(' '.join(result['limitations']))}</p>"
        "</section>"
    )
