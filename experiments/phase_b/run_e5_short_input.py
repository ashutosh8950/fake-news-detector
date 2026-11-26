"""E5: short-input robustness for original and marker-stripped models."""

from pathlib import Path

import numpy as np

from common import ensemble_predictions, fit_models, first_sentences, load_grouped_data, preprocess_batch, preprocess_rows, write_json
from run_e3_marker_stripping import strip_source_markers


def stripped_texts(frame, mode):
    values = []
    for row in frame.itertuples(index=False):
        title, body = strip_source_markers(row.text, row.title)
        if mode == "title_only":
            body = ""
        elif mode == "first_sentence":
            body = first_sentences(body, 1)
        else:
            body = first_sentences(body, 2)
        values.append(__import__("preprocessor").preprocess(title, body))
    return preprocess_batch(values)


def summarize(probabilities, predictions):
    return {"accuracy": float((predictions == LABELS).mean()), "percent_predicted_fake": float((predictions == 0).mean() * 100.0)}


LABELS = None


def main() -> None:
    global LABELS
    train, test, _ = load_grouped_data()
    LABELS = test["label"].to_numpy(dtype=int)
    original_train = preprocess_rows(train)
    stripped_train = preprocess_batch(
        f"{title} {title} {title} {body}"
        for row in train.itertuples(index=False)
        for title, body in [strip_source_markers(row.text, row.title)]
    )
    original_vec, original_models = fit_models(original_train, train["label"])
    stripped_vec, stripped_models = fit_models(stripped_train, train["label"])
    result = {}
    for mode in ("title_only", "first_sentence", "first_two_sentences"):
        original_values = preprocess_batch(
            f"{row.title} {row.title} {row.title} "
            f"{'' if mode == 'title_only' else first_sentences(row.text, 1 if mode == 'first_sentence' else 2)}"
            for row in test.itertuples(index=False)
        )
        stripped_values = stripped_texts(test, mode)
        original_prob, original_pred = ensemble_predictions(original_models, original_vec, original_values)
        stripped_prob, stripped_pred = ensemble_predictions(stripped_models, stripped_vec, stripped_values)
        result[mode] = {"original_model": summarize(original_prob, original_pred), "stripped_model": summarize(stripped_prob, stripped_pred)}
    write_json(Path(__file__).with_name("e5_short_input.json"), {"experiment": "E5", "results": result})


if __name__ == "__main__":
    main()
