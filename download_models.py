"""Stage and verify the calibrated artifact bundle before activating it.

Release assets must be generated with ``python scripts/build_manifest.py``.
The downloaded manifest is verified byte-for-byte before any model is loaded.
"""

from __future__ import annotations

import json
import os
import shutil
import sys
import tempfile
import time
from pathlib import Path

import requests
from loguru import logger

from artifact_contract import (
    MAX_ARTIFACT_BYTES,
    REQUIRED_ARTIFACT_FILES,
    ArtifactVerificationError,
    verify_artifact_bundle,
)
from scripts.build_manifest import build_manifest

GITHUB_RELEASE_URL = "https://github.com/ashutosh8950/fake-news-detector/releases/download/v2.0-calibrated-models"
ARTIFACT_MANIFEST_FILE = "artifact_manifest.json"
CALIBRATION_REPORT_FILE = "phase2_calibration_report.json"
DOWNLOAD_FILES = (ARTIFACT_MANIFEST_FILE, *REQUIRED_ARTIFACT_FILES)
LOCK_WAIT_SECONDS = 120


def models_are_valid(models_dir: str | Path, metadata_dir: str | Path) -> bool:
    models_path = Path(models_dir)
    metadata_path = Path(metadata_dir)
    try:
        verify_artifact_bundle(
            models_path,
            metadata_path / CALIBRATION_REPORT_FILE,
            models_path / ARTIFACT_MANIFEST_FILE,
        )
        return True
    except (ArtifactVerificationError, OSError) as exc:
        logger.warning("Calibrated artifact verification failed: {}", exc)
        return False


def _acquire_lock(lock_path: Path) -> int:
    try:
        return os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError:
        return -1


def _download_to(path: Path, url: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    response = requests.get(url, stream=True, timeout=300)
    response.raise_for_status()
    content_length = response.headers.get("Content-Length")
    if content_length is not None and int(content_length) > MAX_ARTIFACT_BYTES:
        raise RuntimeError(f"Artifact exceeds size limit: {path.name}")
    written = 0
    with path.open("wb") as handle:
        for chunk in response.iter_content(chunk_size=8192):
            if not chunk:
                continue
            written += len(chunk)
            if written > MAX_ARTIFACT_BYTES:
                raise RuntimeError(f"Artifact exceeds size limit: {path.name}")
            handle.write(chunk)


def _activate_staged_bundle(staging_models: Path, staging_metadata: Path, models_dir: Path, metadata_dir: Path) -> None:
    """Replace files only after validation; cross-directory activation is not atomic."""
    backup = Path(tempfile.mkdtemp(prefix=".calibrated-backup-", dir=str(models_dir.parent)))
    moved_new: list[Path] = []
    moved_old: list[tuple[Path, Path]] = []
    targets = [
        (name, models_dir / name, staging_models / name)
        for name in (ARTIFACT_MANIFEST_FILE, *REQUIRED_ARTIFACT_FILES)
        if name != CALIBRATION_REPORT_FILE
    ]
    targets.append((CALIBRATION_REPORT_FILE, metadata_dir / CALIBRATION_REPORT_FILE, staging_metadata / CALIBRATION_REPORT_FILE))
    try:
        for name, destination, staged in targets:
            destination.parent.mkdir(parents=True, exist_ok=True)
            old = backup / name
            if destination.exists():
                old.parent.mkdir(parents=True, exist_ok=True)
                os.replace(destination, old)
                moved_old.append((destination, old))
            os.replace(staged, destination)
            moved_new.append(destination)
    except Exception:
        for destination in moved_new:
            if destination.exists():
                destination.unlink()
        for destination, old in reversed(moved_old):
            if old.exists():
                os.replace(old, destination)
        raise
    finally:
        shutil.rmtree(backup, ignore_errors=True)


def download_models(models_dir: str = "models/calibrated", metadata_dir: str = "evaluation_results") -> bool:
    models_path = Path(models_dir)
    metadata_path = Path(metadata_dir)
    models_path.mkdir(parents=True, exist_ok=True)
    metadata_path.mkdir(parents=True, exist_ok=True)
    lock_path = models_path / ".download_lock"
    lock_fd = _acquire_lock(lock_path)
    if lock_fd == -1:
        logger.info("Another worker is provisioning calibrated artifacts; waiting.")
        deadline = time.monotonic() + LOCK_WAIT_SECONDS
        while time.monotonic() < deadline:
            if models_are_valid(models_path, metadata_path):
                return True
            time.sleep(2)
        return models_are_valid(models_path, metadata_path)

    staging_root = Path(tempfile.mkdtemp(prefix=".calibrated-staging-", dir=str(models_path.parent)))
    staging_models = staging_root / "models"
    staging_metadata = staging_root / "metadata"
    try:
        os.write(lock_fd, b"staging")
        os.close(lock_fd)
        manifest_downloaded = True
        for filename in DOWNLOAD_FILES:
            destination = staging_metadata / filename if filename == CALIBRATION_REPORT_FILE else staging_models / filename
            try:
                _download_to(destination, f"{GITHUB_RELEASE_URL}/{filename}")
            except requests.HTTPError as exc:
                if filename != ARTIFACT_MANIFEST_FILE or exc.response is None or exc.response.status_code != 404:
                    raise
                manifest_downloaded = False
                logger.warning("Release has no manifest; generating one from the downloaded legacy assets")
        if not manifest_downloaded:
            build_manifest(
                staging_models,
                staging_metadata / CALIBRATION_REPORT_FILE,
                staging_models / ARTIFACT_MANIFEST_FILE,
            )
        verify_artifact_bundle(staging_models, staging_metadata / CALIBRATION_REPORT_FILE, staging_models / ARTIFACT_MANIFEST_FILE)
        report = json.loads((staging_metadata / CALIBRATION_REPORT_FILE).read_text(encoding="utf-8"))
        if not isinstance(report, dict) or set(report.get("models", {})) != {"lr", "dt", "gbc", "nb", "svc"}:
            raise ArtifactVerificationError("Calibration report model set is invalid")
        _activate_staged_bundle(staging_models, staging_metadata, models_path, metadata_path)
        return True
    except Exception as exc:
        logger.error("Calibrated artifact bundle was rejected: {}", exc)
        return False
    finally:
        try:
            os.close(lock_fd)
        except OSError:
            pass
        try:
            lock_path.unlink()
        except FileNotFoundError:
            pass
        shutil.rmtree(staging_root, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(0 if download_models() else 1)
