# Verification results and evidence boundary

## What has been validated in this repository

| Item | Method | Evidence | Result boundary |
|---|---|---|---|
| Current-feature maths | Deterministic sinusoid/sideband C++ test | `firmware/test/test_signal_features.cpp` | Confirms RMS, crest factor, Goertzel amplitude, sideband-ratio calculations on synthetic signals. |
| Software fault signatures | Python unit tests on seeded data | `tests/test_features.py` | Confirms the generator creates intentionally different feature patterns. |
| Classifier pipeline | Stratified holdout over generated data | `analysis/train_demo.py` | Confirms an explainable baseline classifier on **modelled**, not measured, conditions. |
| Reproducibility | GitHub Actions | `.github/workflows/ci.yml` | Confirms that analysis and portable C++ tests run from a clean checkout. |

## Physical validation status

No physical motor prototype, reference-instrument calibration, real-motor recordings, or fault-injection experiment is included. Accordingly, this repository makes no claim about field accuracy, fault sensitivity, repeatability on installed sensors, electromagnetic compatibility, enclosure/PCB compliance, or protective shutdown performance. Hardware thresholds and the wiring reference are not safety-validated.

The ESP32-S3 sketch is a firmware bring-up skeleton: it reads the MCU analogue input, while the vibration values are demonstration constants rather than samples from an IMU. Its nominal sampling and feature readouts have not been verified on a physical board.

## Reproduce the synthetic benchmark

```bash
pip install -r requirements.txt
python analysis/train_demo.py --out docs/assets/condition-map.png --metrics docs/assets/demo_metrics.json
cat docs/assets/demo_metrics.json
```

The JSON file is ignored by Git because it is generated in CI/local validation; the plot is retained as a readable project preview.
