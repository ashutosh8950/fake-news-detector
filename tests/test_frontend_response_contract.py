import json
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "frontend" / "response_contract.js"
NODE = shutil.which("node")


pytestmark = pytest.mark.skipif(NODE is None, reason="Node.js is not installed")


def run_contract(mode, payload):
    script = """
const contract = require(process.argv[1]);
const input = JSON.parse(require('fs').readFileSync(0, 'utf8'));
process.stdout.write(JSON.stringify({valid: contract.validate(input.mode, input.payload)}));
"""
    result = subprocess.run(
        [NODE, "-e", script, str(CONTRACT),],
        input=json.dumps({"mode": mode, "payload": payload}),
        text=True,
        capture_output=True,
        check=True,
        cwd=ROOT,
    )
    return json.loads(result.stdout)["valid"]


def valid_ensemble():
    return {
        "ensemble_is_fake": False,
        "ensemble_label": "REAL NEWS",
        "overall_confidence": 92.5,
        "fake_votes": 0,
        "real_votes": 2,
        "total_models": 2,
        "models": {
            "a": {"name": "Model A", "label": "Real", "is_fake": False, "confidence": 90.0},
            "b": {"name": "Model B", "label": "Real", "is_fake": False, "confidence": 95.0},
        },
    }


def test_valid_track_a_and_deep_responses_are_accepted():
    assert run_contract("ensemble", valid_ensemble()) is True
    assert run_contract("deep", {"label": "Real", "confidence": 88.0, "processing_time_ms": 12.0}) is True


@pytest.mark.parametrize(
    "payload",
    [
        None,
        {},
        {"ensemble_is_fake": False, "ensemble_label": "REAL NEWS"},
        {**valid_ensemble(), "models": []},
        {**valid_ensemble(), "overall_confidence": "92"},
        {**valid_ensemble(), "ensemble_label": "UNKNOWN"},
    ],
)
def test_malformed_ensemble_responses_are_rejected(payload):
    assert run_contract("ensemble", payload) is False


def test_invalid_deep_response_is_rejected():
    assert run_contract("deep", {"label": "UNKNOWN", "confidence": 88.0}) is False
    assert run_contract("deep", {"label": "Real", "confidence": 101.0}) is False
