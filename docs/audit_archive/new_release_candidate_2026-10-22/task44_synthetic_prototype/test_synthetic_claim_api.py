import unittest

from synthetic_claim_api import (
    ContractError,
    forbid_track_a_conversion,
    render_mock_ui,
    run_synthetic_fixture,
    validate_request,
    validate_response,
)


BASE = {"claim": "Synthetic supported claim", "evidence_mode": "required"}


def response(outcome="SUPPORTED", evidence=None):
    return {
        "track": "claim_verifier",
        "task": "fever_claim_verification",
        "outcome": outcome,
        "score": 0.9 if outcome != "INSUFFICIENT_EVIDENCE" else 0.0,
        "evidence": evidence if evidence is not None else [{"source_id": "SYNTHETIC-ONLY", "title": "Synthetic title", "snippet": "Synthetic evidence text."}],
        "limitations": ["Synthetic fixture only."],
        "disclaimer": "Not an authoritative fact-check.",
    }


class SyntheticContractTests(unittest.TestCase):
    def test_all_three_outcomes(self):
        self.assertEqual(run_synthetic_fixture(BASE, synthetic_mode=True)["outcome"], "SUPPORTED")
        self.assertEqual(run_synthetic_fixture({**BASE, "claim": "Synthetic refuted claim"}, synthetic_mode=True)["outcome"], "REFUTED")
        self.assertEqual(run_synthetic_fixture({**BASE, "claim": "Unknown synthetic claim"}, synthetic_mode=True)["outcome"], "INSUFFICIENT_EVIDENCE")

    def test_valid_request_and_strict_fields(self):
        self.assertEqual(validate_request(BASE)["claim"], BASE["claim"])
        for payload in (
            {**BASE, "unexpected": True},
            {"claim": BASE["claim"]},
            {"evidence_mode": "required"},
            None,
            [],
            "not an object",
        ):
            with self.subTest(payload=payload):
                with self.assertRaises(ContractError):
                    validate_request(payload)

    def test_empty_and_oversized_claims_fail(self):
        with self.assertRaises(ContractError):
            validate_request({**BASE, "claim": "   "})
        with self.assertRaises(ContractError):
            validate_request({**BASE, "claim": "x" * 4001})

    def test_missing_evidence_is_first_class(self):
        result = run_synthetic_fixture({**BASE, "claim": "Unknown synthetic claim"}, synthetic_mode=True)
        self.assertEqual(result["outcome"], "INSUFFICIENT_EVIDENCE")
        self.assertEqual(result["evidence"], [])
        for malformed in (
            {key: value for key, value in result.items() if key != "evidence"},
            {**result, "evidence": None},
            {**result, "evidence": "not a list"},
            {**result, "evidence": [{"source_id": "fake"}]},
        ):
            with self.subTest(malformed=malformed):
                with self.assertRaises(ContractError):
                    validate_response(malformed)

    def test_positive_outcomes_require_evidence(self):
        with self.assertRaises(ContractError):
            validate_response(response("SUPPORTED", []))
        with self.assertRaises(ContractError):
            validate_response(response("REFUTED", []))
        self.assertEqual(validate_response(response("SUPPORTED"))["outcome"], "SUPPORTED")
        self.assertEqual(validate_response(response("REFUTED"))["outcome"], "REFUTED")

    def test_evidence_items_are_strictly_validated(self):
        for item in (
            1,
            None,
            {"snippet": ""},
            {"snippet": "   "},
            {"title": "missing snippet"},
            {"snippet": "ok"},
            {"source_id": "SYNTHETIC", "snippet": "ok", "extra": "no"},
            {"source_id": 7, "snippet": "ok"},
            {"source_id": "SYNTHETIC", "snippet": "ok", "source_url": 7},
            {"source_id": "SYNTHETIC", "snippet": "ok", "source_version": "   "},
        ):
            with self.subTest(item=item):
                with self.assertRaises(ContractError):
                    validate_response(response("SUPPORTED", [item]))
        self.assertEqual(validate_response(response("INSUFFICIENT_EVIDENCE", []))["evidence"], [])

    def test_source_id_and_snippet_whitespace_are_rejected(self):
        for item in (
            {"source_id": "", "snippet": "ok"},
            {"source_id": "   ", "snippet": "ok"},
            {"source_id": "SYNTHETIC", "snippet": ""},
            {"source_id": "SYNTHETIC", "snippet": "   "},
        ):
            with self.subTest(item=item):
                with self.assertRaises(ContractError):
                    validate_response(response("SUPPORTED", [item]))

    def test_metadata_length_limits_are_enforced(self):
        limits = (
            ("source_id", 200),
            ("title", 300),
            ("snippet", 2000),
            ("source_url", 2048),
            ("source_version", 200),
            ("retrieved_at", 100),
        )
        base_item = {"source_id": "SYNTHETIC", "snippet": "ok"}
        for field, limit in limits:
            at_limit = {**base_item, field: "x" * limit}
            self.assertIsNotNone(validate_response(response("SUPPORTED", [at_limit])))
            beyond_limit = {**base_item, field: "x" * (limit + 1)}
            with self.subTest(field=field):
                with self.assertRaises(ContractError):
                    validate_response(response("SUPPORTED", [beyond_limit]))

    def test_evidence_provenance_metadata_is_accepted_when_well_formed(self):
        item = {
            "source_id": "SYNTHETIC-ONLY",
            "title": "Synthetic title",
            "snippet": "Synthetic evidence text.",
            "source_url": "synthetic://fixture/source-1",
            "source_version": "fixture-v1",
            "retrieved_at": "synthetic-time",
        }
        validated = validate_response(response("SUPPORTED", [item]))
        self.assertEqual(validated["evidence"][0]["source_id"], "SYNTHETIC-ONLY")

    def test_hostile_strings_are_escaped(self):
        hostile = '<script>alert("x")</script> & <img src=x onerror="bad">'
        result = response("SUPPORTED", [{"source_id": hostile, "title": hostile, "snippet": hostile}])
        html = render_mock_ui(result)
        self.assertNotIn("<script>", html)
        self.assertNotIn("<img", html)
        self.assertIn("&lt;script&gt;", html)
        self.assertIn("&lt;img", html)

    def test_invalid_ui_response_returns_controlled_error(self):
        html = render_mock_ui({**response("SUPPORTED", []), "evidence": [1]})
        self.assertIn("data-state='error'", html)
        self.assertIn("Invalid claim-verification response.", html)
        self.assertNotIn("Traceback", html)

    def test_unknown_outcome_and_extra_response_fields_fail(self):
        result = run_synthetic_fixture(BASE, synthetic_mode=True)
        for outcome in ("FAKE", "REAL", "Fake", "Real", "UNKNOWN", ""):
            with self.subTest(outcome=outcome):
                with self.assertRaises(ContractError):
                    validate_response({**result, "outcome": outcome})
        with self.assertRaises(ContractError):
            validate_response({**result, "debug": "no"})

    def test_invalid_responses_cannot_silently_become_successful_verdicts(self):
        result = run_synthetic_fixture(BASE, synthetic_mode=True)
        invalid_responses = (
            {**result, "outcome": "SUPPORTED", "evidence": []},
            {**result, "outcome": "REFUTED", "evidence": []},
            {**result, "outcome": "FAKE"},
            {**result, "outcome": "REAL"},
            {**result, "score": "0.9"},
            {**result, "limitations": None},
        )
        for payload in invalid_responses:
            with self.subTest(payload=payload):
                with self.assertRaises(ContractError):
                    validate_response(payload)

    def test_conversion_to_track_a_is_forbidden(self):
        with self.assertRaises(ContractError):
            forbid_track_a_conversion("REFUTED")
        with self.assertRaises(ContractError):
            forbid_track_a_conversion("INSUFFICIENT_EVIDENCE")

    def test_production_and_default_modes_are_disabled(self):
        with self.assertRaises(ContractError):
            run_synthetic_fixture(BASE)
        with self.assertRaises(ContractError):
            run_synthetic_fixture(BASE, environment="production", synthetic_mode=True)

    def test_ui_is_explicitly_synthetic_and_escaped(self):
        result = run_synthetic_fixture(BASE, synthetic_mode=True)
        html = render_mock_ui(result)
        self.assertIn("SYNTHETIC-ONLY-1", html)
        self.assertIn("not an authoritative fact-check", html)
        self.assertIn("data-track='claim-verifier'", html)


if __name__ == "__main__":
    unittest.main()
