"""E1: fast-model baseline on the fixed duplicate-aware grouped split."""

from common import evaluate_models, fit_models, load_grouped_data, preprocess_rows, write_json


def main() -> None:
    train, test, _ = load_grouped_data()
    train_text = preprocess_rows(train, light=True)
    test_text = preprocess_rows(test, light=True)
    vec, models = fit_models(train_text, train["label"])
    metrics = evaluate_models(models, vec, test_text, test["label"])
    light_vec, light_models = fit_models(preprocess_rows(train, light=True), train["label"])
    metrics["light_preprocessor"] = evaluate_models(light_models, light_vec, preprocess_rows(test, light=True), test["label"])
    write_json(
        __import__("pathlib").Path(__file__).with_name("e1_baseline.json"),
        {"experiment": "E1", "preprocessor": "light (cleaning + stopwords, no lemmatization)", "split": "final_v5 primary grouped split", "models": metrics},
    )


if __name__ == "__main__":
    main()
