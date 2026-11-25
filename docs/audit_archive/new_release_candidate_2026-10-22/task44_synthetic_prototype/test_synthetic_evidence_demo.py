import unittest

from synthetic_claim_api import ContractError, validate_response
from synthetic_evidence_demo import build_demo_results


class SyntheticEvidenceDemoTests(unittest.TestCase):
    def test_demo_contains_all_three_permitted_outcomes(self):
        results = build_demo_results()
        self.assertEqual(
            {item["assigned_outcome"] for item in results},
            {"SUPPORTED", "REFUTED", "INSUFFICIENT_EVIDENCE"},
        )

    def test_every_example_is_explicitly_synthetic_and_auditable(self):
        for item in build_demo_results():
            with self.subTest(example_id=item["example_id"]):
                self.assertTrue(item["synthetic"])
                self.assertIn("synthetic", item["claim"].lower())
                self.assertTrue(item["evidence_rationale"])
                self.assertEqual(item["assigned_outcome"], item["response"]["outcome"])
                if item["response"]["evidence"]:
                    self.assertIn("SYNTHETIC-ONLY", json_source_ids(item["response"]))

    def test_insufficient_example_has_no_evidence(self):
        item = next(x for x in build_demo_results() if x["assigned_outcome"] == "INSUFFICIENT_EVIDENCE")
        self.assertEqual(item["response"]["evidence"], [])

    def test_invalid_evidence_cannot_be_converted_to_success(self):
        item = next(x for x in build_demo_results() if x["assigned_outcome"] == "SUPPORTED")
        invalid = {**item["response"], "evidence": [{"source_id": "SYNTHETIC-ONLY-BAD"}]}
        with self.assertRaises(ContractError):
            validate_response(invalid)


def json_source_ids(response):
    return " ".join(item.get("source_id", "") for item in response["evidence"])


if __name__ == "__main__":
    unittest.main()
