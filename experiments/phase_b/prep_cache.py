"""Build and load the resumable, outside-repository spaCy audit cache."""

from __future__ import annotations

import hashlib
import os
import pickle
import sys
import tempfile
from pathlib import Path
from typing import Iterable, Iterator

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from preprocessor import clean_text, nlp  # noqa: E402

DATA_DIR = ROOT / "data"
CACHE_ROOT = Path(tempfile.gettempdir()) / "fake_news_detector_phase_b"
CACHE_VERSION = "spacy_pipe_v2"


def _input_hash() -> str:
    digest = hashlib.sha256(CACHE_VERSION.encode())
    for path in (DATA_DIR / "Fake.csv", DATA_DIR / "True.csv", ROOT / "preprocessor.py"):
        digest.update(path.read_bytes())
    return digest.hexdigest()[:20]


def cache_path() -> Path:
    CACHE_ROOT.mkdir(parents=True, exist_ok=True)
    return CACHE_ROOT / f"spacy_{_input_hash()}.pkl"


def _records() -> list[tuple[str, str]]:
    records = []
    for filename, prefix in (("Fake.csv", "fake"), ("True.csv", "true")):
        frame = pd.read_csv(DATA_DIR / filename).fillna("")
        for index, row in frame.iterrows():
            title, text = str(row["title"]), str(row["text"])
            records.append((f"{prefix}:{index}", f"{title} {title} {title} {text}"))
    return records


def _lemmatize(cleaned: Iterable[str]) -> Iterator[str]:
    workers = max(1, (os.cpu_count() or 1) - 1)
    for doc in nlp.pipe(cleaned, batch_size=500, n_process=workers):
        yield " ".join(token.lemma_ for token in doc if not token.is_stop and len(token.text) > 2)


def ensure_cache() -> Path:
    records = _records()
    path = cache_path()
    partial = path.with_suffix(".partial.pkl")
    try:
        completed = pickle.loads(partial.read_bytes())
    except (FileNotFoundError, EOFError, pickle.PickleError):
        completed = {}
    missing = [(row_id, value) for row_id, value in records if row_id not in completed]
    if missing:
        print(f"spaCy cache: {len(completed)}/{len(records)} rows already complete", flush=True)
        for index, (row_id, value) in enumerate(zip(missing, _lemmatize(clean_text(value) for _, value in missing)), 1):
            completed[row_id[0]] = value
            if index % 1000 == 0:
                partial.write_bytes(pickle.dumps(completed, protocol=pickle.HIGHEST_PROTOCOL))
                print(f"spaCy cache: {len(completed)}/{len(records)} rows", flush=True)
        partial.write_bytes(pickle.dumps(completed, protocol=pickle.HIGHEST_PROTOCOL))
    path.write_bytes(pickle.dumps(completed, protocol=pickle.HIGHEST_PROTOCOL))
    partial.unlink(missing_ok=True)
    print(f"spaCy cache ready: {path}", flush=True)
    return path


def load_cache() -> dict[str, str]:
    path = cache_path()
    if not path.exists():
        ensure_cache()
    return pickle.loads(path.read_bytes())


def light_preprocess(title: str = "", text: str = "") -> str:
    """Use production cleaning and stopword filtering, without lemmatization."""
    cleaned = clean_text(f"{title} {title} {title} {text}")
    stop_words = nlp.Defaults.stop_words
    return " ".join(token for token in cleaned.split() if token not in stop_words and len(token) > 2)


if __name__ == "__main__":
    ensure_cache()
