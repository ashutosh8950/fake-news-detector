# Calibrated artifact release

The production loader accepts only the five calibrated classifiers, the TF-IDF
vectorizer, the calibration report, and a manifest created from those exact
bytes.

Build and verify the manifest after producing or receiving the artifacts:

```powershell
python scripts/build_manifest.py
```

Upload these files to the `v2.0-calibrated-models` GitHub Release:

```text
artifact_manifest.json
vectorizer.pkl
lr_calibrated.pkl
dt_calibrated.pkl
gbc_calibrated.pkl
nb_calibrated.pkl
svc_calibrated.pkl
phase2_calibration_report.json
```

`download_models.py` downloads the same seven files into staging, verifies the
manifest hashes and sizes before deserializing anything, and activates the
bundle only after verification succeeds. A fresh deployment therefore uses the
same manifest contract as a local build.
