"""Generate the exact Phase 1 held-out split without fitting models."""

import os

import numpy as np
from sklearn.model_selection import train_test_split

from evaluate_pipeline import HELD_OUT_FRACTION, HELD_OUT_PATH, RANDOM_STATE, load_dataset


def main() -> None:
    data = load_dataset()
    _, held_out_indices = train_test_split(
        np.arange(len(data)),
        test_size=HELD_OUT_FRACTION,
        random_state=RANDOM_STATE,
        stratify=data["class"],
    )
    os.makedirs(os.path.dirname(HELD_OUT_PATH), exist_ok=True)
    data.iloc[held_out_indices][["title", "text", "class"]].to_csv(
        HELD_OUT_PATH, index=False
    )
    print(f"Saved {len(held_out_indices):,} rows to {HELD_OUT_PATH}")


if __name__ == "__main__":
    main()
