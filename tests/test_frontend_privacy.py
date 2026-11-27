from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP_JS = ROOT / "frontend" / "app.js"


def _source() -> str:
    return APP_JS.read_text(encoding="utf-8")


def _function_body(source: str, name: str) -> str:
    marker = f"function {name}"
    start = source.index(marker)
    next_function = source.find("\nfunction ", start + len(marker))
    return source[start:] if next_function == -1 else source[start:next_function]


def test_history_content_is_not_loaded_or_persisted():
    source = _source()
    record_body = _function_body(source, "recordAnalysis")

    assert "history: []," in source
    assert "localStorage.removeItem(STORAGE.history);" in source
    assert "snippetSource" not in source
    assert "saveJSON(STORAGE.history" not in record_body
    assert "recordAnalysis(result);" in source


def test_legacy_history_is_retired_without_clearing_unrelated_storage():
    source = _source()

    assert "localStorage.removeItem(STORAGE.history);" in source
    assert "localStorage.getItem(STORAGE.theme)" in source
    assert "saveJSON(STORAGE.stats, state.stats);" in source
    assert "localStorage.clear()" not in source


def test_history_rendering_uses_generic_session_text_not_persisted_content():
    source = _source()
    render_body = _function_body(source, "renderHistory")

    assert "Article analyzed in this session" in render_body
    assert "h.snippet" not in render_body
    assert "escapeHtml(h.snippet)" not in render_body
