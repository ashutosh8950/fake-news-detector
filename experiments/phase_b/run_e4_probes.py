"""E4: title, short body, style-only, and character-prefix probes."""

from pathlib import Path

import numpy as np
from common import classification_metrics, load_grouped_data, preprocess_rows, write_json
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression


def style_features(values):
    output = []
    for text in values:
        words = text.split()
        chars = max(len(text), 1)
        output.append(
            [
                len(text),
                len(words),
                text.count("!"),
                text.count("?"),
                text.count("."),
                sum(char.isupper() for char in text) / chars,
                sum(char.isdigit() for char in text) / chars,
                sum(not char.isalnum() and not char.isspace() for char in text) / chars,
            ]
        )
    return np.asarray(output, dtype=float)


def text_probe(train_values, test_values, labels_train, labels_test, analyzer="word"):
    vec = TfidfVectorizer(
        analyzer=analyzer,
        ngram_range=(3, 5) if analyzer == "char" else (1, 2),
        min_df=2,
        max_features=50_000,
    )
    train_matrix = vec.fit_transform(train_values)
    test_matrix = vec.transform(test_values)
    model = LogisticRegression(max_iter=1000, random_state=42)
    model.fit(train_matrix, labels_train)
    probabilities = model.predict_proba(test_matrix)[:, 1]
    return classification_metrics(
        np.asarray(labels_test), (probabilities >= 0.5).astype(int), probabilities
    )


def main() -> None:
    train, test, _ = load_grouped_data()
    labels_train, labels_test = train["label"], test["label"]
    title_train, title_test = (
        preprocess_rows(train, title_only=True, light=True),
        preprocess_rows(test, title_only=True, light=True),
    )
    body_train = preprocess_rows(train, body_chars=300, light=True)
    body_test = preprocess_rows(test, body_chars=300, light=True)
    char_train = [row.text[:50] for row in train.itertuples(index=False)]
    char_test = [row.text[:50] for row in test.itertuples(index=False)]
    style_train = style_features([row.text for row in train.itertuples(index=False)])
    style_test = style_features([row.text for row in test.itertuples(index=False)])
    style_model = LogisticRegression(max_iter=1000, random_state=42).fit(style_train, labels_train)
    style_prob = style_model.predict_proba(style_test)[:, 1]
    result = {
        "title_only": text_probe(title_train, title_test, labels_train, labels_test),
        "body_first_300": text_probe(body_train, body_test, labels_train, labels_test),
        "style_only": classification_metrics(
            np.asarray(labels_test), (style_prob >= 0.5).astype(int), style_prob
        ),
        "char_first_50": text_probe(
            char_train, char_test, labels_train, labels_test, analyzer="char"
        ),
    }
    write_json(Path(__file__).with_name("e4_probes.json"), {"experiment": "E4", "probes": result})


if __name__ == "__main__":
    main()
