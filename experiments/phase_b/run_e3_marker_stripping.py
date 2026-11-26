"""E3: remove source/format markers and measure train/test mismatch effects."""

from pathlib import Path
import re

from common import evaluate_models, fit_models, light_preprocess, load_grouped_data, preprocess_rows, write_json


def strip_source_markers(text: str, title: str = "") -> tuple[str, str]:
    """Remove common outlet, dateline, byline, social, and image boilerplate."""
    outlet = r"(?:Reuters|Associated Press|AP News|CNN|Fox News|The New York Times|21st Century Wire|Getty Images)"
    def clean(value: str) -> str:
        value = re.sub(r"https?://\S+|www\.\S+|pic\.twitter\.com/\S+", " ", value, flags=re.I)
        value = re.sub(r"@\w+", " ", value)
        value = re.sub(r"^\s*(?:[A-Z][A-Z .,'/-]{2,40}\s+)?\(" + outlet + r"\)\s*[-:–—]?\s*", " ", value, flags=re.I)
        value = re.sub(r"^\s*(?:By|BY)\s+[A-Z][^\n:]{2,100}\s*[:\-–—]\s*", " ", value)
        value = re.sub(r"^\s*[A-Z][A-Z .,'/-]{2,40}\s+[-–—]\s+", " ", value)
        value = re.sub(r"(?:featured image|image via|image credit|photo by|getty images|read more)\s*[:\-–—]?", " ", value, flags=re.I)
        value = re.sub(outlet, " ", value, flags=re.I)
        value = re.sub(r"\s+", " ", value).strip()
        return value
    return clean(title), clean(text)


def stripped_rows(frame):
    titles, bodies = [], []
    for row in frame.itertuples(index=False):
        title, body = strip_source_markers(row.text, row.title)
        titles.append(title)
        bodies.append(body)
    return [light_preprocess(t, b) for t, b in zip(titles, bodies)]


def run(train_text, test_text, train, test):
    vec, models = fit_models(train_text, train["label"])
    return evaluate_models(models, vec, test_text, test["label"])


def main() -> None:
    train, test, _ = load_grouped_data()
    original_train, original_test = preprocess_rows(train, light=True), preprocess_rows(test, light=True)
    stripped_train, stripped_test = stripped_rows(train), stripped_rows(test)
    conditions = {
        "original_train_original_test": run(original_train, original_test, train, test),
        "stripped_train_stripped_test": run(stripped_train, stripped_test, train, test),
        "original_train_stripped_test": run(original_train, stripped_test, train, test),
        "stripped_train_original_test": run(stripped_train, original_test, train, test),
    }
    examples = []
    for row in test.head(10).itertuples(index=False):
        new_title, new_text = strip_source_markers(row.text, row.title)
        examples.append({"before_title": row.title, "after_title": new_title, "before_text": row.text[:300], "after_text": new_text[:300]})
    baseline = conditions["original_train_original_test"]
    drops = {}
    for condition, values in conditions.items():
        drops[condition] = {key: values[key]["accuracy"] - baseline[key]["accuracy"] for key in baseline}
    write_json(Path(__file__).with_name("e3_marker_stripping.json"), {"experiment": "E3", "conditions": conditions, "accuracy_delta_vs_e1": drops, "examples": examples})


if __name__ == "__main__":
    main()
