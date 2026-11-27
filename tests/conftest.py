"""Shared test policy: no downloads and explicit artifact-dependent skips."""

import faulthandler
import multiprocessing
import threading
from pathlib import Path

import pytest


def pytest_sessionfinish(session, exitstatus):
    """Temporary diagnosis for processes surviving pytest session teardown."""
    del session, exitstatus
    print("\n[sessionfinish] threads:")
    for thread in threading.enumerate():
        print(
            f"  name={thread.name!r} daemon={thread.daemon} alive={thread.is_alive()}"
        )
    print("[sessionfinish] multiprocessing children:")
    for child in multiprocessing.active_children():
        print(f"  name={child.name!r} pid={child.pid} alive={child.is_alive()}")
    faulthandler.dump_traceback_later(30, exit=True)


def _calibrated_bundle_is_present() -> bool:
    models = Path("models/calibrated")
    required = {
        "artifact_manifest.json",
        "vectorizer.pkl",
        "lr_calibrated.pkl",
        "dt_calibrated.pkl",
        "gbc_calibrated.pkl",
        "nb_calibrated.pkl",
        "svc_calibrated.pkl",
    }
    return required.issubset({path.name for path in models.glob("*")})


def pytest_configure(config):
    config.addinivalue_line(
        "markers",
        "requires_artifacts: test requires local calibrated models and/or dataset files",
    )


def pytest_collection_modifyitems(config, items):
    del config
    missing_models = not _calibrated_bundle_is_present()
    missing_data = not Path("data").is_dir()
    for item in items:
        if "requires_artifacts" not in item.keywords:
            continue
        reasons = []
        if missing_models:
            reasons.append("local calibrated model bundle is missing or incomplete")
        if missing_data:
            reasons.append("local data/ directory is missing")
        if reasons:
            item.add_marker(pytest.mark.skip(reason="; ".join(reasons)))


