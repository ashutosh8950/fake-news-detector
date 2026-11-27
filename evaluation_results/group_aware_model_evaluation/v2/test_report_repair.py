import pandas as pd
import pytest

from report_repair import repair_confusion_matrices


def test_confusion_matrix_serialization_is_numeric_and_axis_ordered():
    predictions = pd.DataFrame(
        {
            "policy": ["p"] * 4,
            "label": [0, 0, 1, 1],
            "uncalibrated_prediction": [0, 1, 0, 1],
            "calibrated_prediction": [0, 0, 1, 1],
        }
    )
    metrics = {
        "p": {
            "uncalibrated": {"confusion_matrix_class_order_0_fake_1_real": [[1, 1], [1, 1]]},
            "calibrated": {"confusion_matrix_class_order_0_fake_1_real": [[2, 0], [0, 2]]},
        }
    }
    result = repair_confusion_matrices(predictions, metrics)
    assert result["p"]["uncalibrated"]["matrix"] == [[1, 1], [1, 1]]
    assert result["p"]["calibrated"]["matrix"] == [[2, 0], [0, 2]]
    assert result["p"]["calibrated"]["axis_order"] == ["Fake", "Real"]
    assert result["p"]["calibrated"]["matrix"] is not None


def test_confusion_matrix_mismatch_or_null_cannot_pass():
    predictions = pd.DataFrame(
        {"policy": ["p", "p"], "label": [0, 1], "uncalibrated_prediction": [0, 1], "calibrated_prediction": [0, 1]}
    )
    metrics = {
        "p": {
            "uncalibrated": {"confusion_matrix_class_order_0_fake_1_real": None},
            "calibrated": {"confusion_matrix_class_order_0_fake_1_real": [[1, 0], [0, 1]]},
        }
    }
    with pytest.raises(AssertionError):
        repair_confusion_matrices(predictions, metrics)
