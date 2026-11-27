"""E2: inspect the highest-weight Logistic Regression features."""

from pathlib import Path

from common import fit_models, load_grouped_data, preprocess_rows, write_json

ARTIFACT_TERMS = (
    "reuters",
    "21st century wire",
    "pic twitter",
    "featured image",
    "image via",
    "getty",
    "read more",
    "associated press",
    "cnn",
    "byline",
    "washington",
    "london",
    "new york",
    "monday",
    "tuesday",
    "wednesday",
    "thursday",
    "friday",
)


def is_artifact(feature: str) -> bool:
    normalized = feature.lower()
    return any(term in normalized for term in ARTIFACT_TERMS)


def main() -> None:
    train, _, _ = load_grouped_data()
    vec, models = fit_models(preprocess_rows(train), train["label"])
    model = models["lr"]
    names = vec.get_feature_names_out()
    weights = model.coef_[0]
    result = {}
    for label, indices in (
        ("fake", weights.argsort()[:50]),
        ("real", weights.argsort()[-50:][::-1]),
    ):
        features = [
            {
                "feature": str(names[i]),
                "weight": float(weights[i]),
                "artifact": is_artifact(str(names[i])),
            }
            for i in indices
        ]
        result[label] = {
            "features": features,
            "artifact_percent": 100.0 * sum(item["artifact"] for item in features) / 50.0,
        }
    write_json(
        Path(__file__).with_name("e2_top_features.json"),
        {"experiment": "E2", "logistic_regression": result},
    )


if __name__ == "__main__":
    main()
