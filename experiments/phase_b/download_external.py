"""Download Phase B external datasets to experiments/phase_b/external/.

Run locally with:
    python -m pip install datasets pyarrow pandas
    python experiments/phase_b/download_external.py

Dataset metadata and intended mapping:
* polsci/fake-news — https://huggingface.co/datasets/polsci/fake-news
  GPL on the dataset card; legit -> 1 (real), fake -> 0. Short examples; verify
  upstream terms and provenance before commercial redistribution.
* fauxNeuz/RealFakeNews — https://huggingface.co/datasets/fauxNeuz/RealFakeNews
  CC BY-NC-SA 4.0; REAL -> 1, FAKE -> 0. Non-commercial/share-alike only.
* magnea/fake-news-formated — https://huggingface.co/datasets/magnea/fake-news-formated
  Apache-2.0 on the dataset card; real/true/1 -> 1, fake/false/0 -> 0.
  Aggregated upstream sources, so provenance and possible ISOT overlap must be
  checked before treating it as independent external evidence.

The script does not claim that any dataset is suitable for commercial use or
independent evaluation without reviewing its upstream provenance.
"""

from pathlib import Path

from datasets import load_dataset

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "experiments" / "phase_b" / "external"
DATASETS = {
    "polsci_fake_news": "polsci/fake-news",
    "realfakenews": "fauxNeuz/RealFakeNews",
    "fake_news_formated": "magnea/fake-news-formated",
}


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for name, dataset_id in DATASETS.items():
        dataset = load_dataset(dataset_id, split="train")
        destination = OUT / f"{name}.parquet"
        dataset.to_parquet(destination)
        print(f"{name}: rows={len(dataset)} columns={dataset.column_names} path={destination}")


if __name__ == "__main__":
    main()
