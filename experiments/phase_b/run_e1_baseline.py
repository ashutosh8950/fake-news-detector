"""E1: fast-model baseline on the fixed duplicate-aware grouped split."""

from common import evaluate_models, fit_models, load_grouped_data, preprocess_rows, write_json


def main() -> None:
    train, test, _ = load_grouped_data()
    train_text = preprocess_rows(train)
    test_text = preprocess_rows(test)
    vec, models = fit_models(train_text, train["label"])
    metrics = evaluate_models(models, vec, test_text, test["label"])
    write_json(
        __import__("pathlib").Path(__file__).with_name("e1_baseline.json"),
        {"experiment": "E1", "split": "final_v5 primary grouped split", "models": metrics},
    )


if __name__ == "__main__":
    main()
