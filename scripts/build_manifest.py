"""Build the trusted manifest for an existing calibrated artifact bundle.

This script only hashes existing artifacts. It does not train models or change
their serialized contents.
"""

from __future__ import annotations

import argparse
import json
import platform
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from artifact_contract import (  # noqa: E402
    ARTIFACT_MANIFEST_SCHEMA,
    REQUIRED_ARTIFACT_FILES,
    sha256_file,
    verify_artifact_bundle,
)


def _versions() -> dict[str, str]:
    versions = {"python": platform.python_version()}
    for module_name in ("numpy", "pandas", "sklearn", "spacy"):
        try:
            module = __import__(module_name)
            versions[module_name] = str(getattr(module, "__version__", "unknown"))
        except ImportError:
            versions[module_name] = "not-installed"
    return versions


def build_manifest(models_dir: Path, report_path: Path, output_path: Path) -> dict[str, object]:
    models_dir = models_dir.resolve()
    report_path = report_path.resolve()
    output_path = output_path.resolve()
    artifacts: dict[str, dict[str, object]] = {}
    for name in REQUIRED_ARTIFACT_FILES:
        path = report_path if name == "phase2_calibration_report.json" else models_dir / name
        if not path.is_file():
            raise FileNotFoundError(f"Required artifact is missing: {path}")
        artifacts[name] = {
            "sha256": sha256_file(path),
            "size_bytes": path.stat().st_size,
        }

    payload: dict[str, object] = {
        "schema_version": ARTIFACT_MANIFEST_SCHEMA,
        "artifacts": artifacts,
        "environment": _versions(),
        "calibration_report_sha256": artifacts["phase2_calibration_report.json"]["sha256"],
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    verify_artifact_bundle(models_dir, report_path, output_path)
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--models-dir", type=Path, default=Path("models/calibrated"))
    parser.add_argument(
        "--report", type=Path, default=Path("evaluation_results/phase2_calibration_report.json")
    )
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args()
    output = args.output or args.models_dir / "artifact_manifest.json"
    payload = build_manifest(args.models_dir, args.report, output)
    print(f"Wrote verified manifest: {output}")
    print(f"Schema: {payload['schema_version']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
