
from preprocessor import preprocess


def test_empty_whitespace_and_malformed_values_follow_current_contract():
    assert preprocess("", "") == ""
    assert preprocess("   ", "\t\n") == ""
    # preprocess interpolates non-strings before clean_text; these values become
    # removable content under the current production implementation.
    assert preprocess(None, None) == ""
    assert preprocess(123, 456) == ""


def test_cleaning_removes_urls_html_brackets_punctuation_and_numbers():
    result = preprocess("Title https://example.com", "<b>Dogs</b> [ignore] cats, 123 42")
    assert result == "title title title dog cat"


def test_unicode_and_non_latin_behavior_is_explicit():
    assert preprocess("Café 中文", "naïve résumé 東京") == "caf caf caf nave rsum"


def test_stop_words_short_tokens_and_lemmatization():
    assert preprocess("Running cats", "The running cats are quickly running") == (
        "run cat run cat run cat run cat quickly run"
    )


def test_title_is_repeated_three_times_before_body():
    result = preprocess("Running cats", "quickly running")
    assert result.split()[:6] == ["run", "cat", "run", "cat", "run", "cat"]
    assert result.split()[-2:] == ["quickly", "run"]


def test_repeated_calls_are_deterministic():
    title = "Representative election headline"
    body = "The candidates discussed policy and accountability."
    assert preprocess(title, body) == preprocess(title, body)
