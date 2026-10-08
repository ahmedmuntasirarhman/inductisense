# Validation plan and evidence boundary

## What has been validated in this repository

| Item | Method | Evidence | Result boundary |
|---|---|---|---|
| Current-feature maths | Deterministic sinusoid/sideband C++ test | `firmware/test/test_signal_features.cpp` | Confirms RMS, crest factor, Goertzel amplitude, sideband-ratio calculations on synthetic signals. |
| Software fault signatures | Python unit tests on seeded data | `tests/test_features.py` | Confirms the generator creates intentionally different feature patterns. |
| Classifier pipeline | Stratified holdout over generated data | `analysis/train_demo.py` | Confirms an explainable baseline classifier on **modelled**, not measured, conditions. |
| Reproducibility | GitHub Actions | `.github/workflows/ci.yml` | Confirms that analysis and portable C++ tests run from a clean checkout. |

## What has **not** been validated yet

- Accuracy on a physical motor.
- Sensor gain/phase calibration against a reference meter.
- Fault sensitivity across motor sizes, loads, or supply conditions.
- Electromagnetic compatibility, enclosure design, or PCB safety compliance.
- Any protective or automatic shutdown use case.

## Field-validation experiment

### Equipment

- Bench induction motor with documented normal operating condition.
- InductiSense prototype, mounted in an insulated enclosure.
- Split-core CT selected for the motor current range.
- Reference current/power analyser and a calibrated accelerometer or vibration meter.
- Load fixture and a supervised, reversible alignment adjustment where permitted.

### Protocol

1. **Baseline:** acquire at least 20 one-minute recordings at three stable loads. Record line frequency, temperature, IMU location, and reference values.
2. **Repeatability:** remove and reinstall the CT and IMU five times; compare RMS and band-ratio change to quantify installation sensitivity.
3. **Controlled perturbation:** under qualified supervision, introduce exactly one reversible condition (e.g., small alignment offset) while keeping load and supply constant.
4. **Blinded analysis:** label recordings only after feature extraction and threshold selection have been locked.
5. **Comparison:** compare InductiSense trends with the reference analyser and inspection findings. Store raw time series and analysis scripts with commit hash.

### Initial acceptance criteria

| Metric | Target | Rationale |
|---|---:|---|
| Current RMS error vs reference | ≤ 5% after calibration | Adequate for a prototype load-context channel. |
| Repeatability of sideband ratio | CV ≤ 15% at fixed condition | Avoids thresholds dominated by sensor reinstallation. |
| Misalignment cue | `2×/1×` ratio increases relative to baseline | Measures directional change rather than a universal threshold. |
| False alerts in stable healthy baseline | 0 alerts in 20 windows | Basic screening reliability gate before exploring sensitivity. |
| Evidence traceability | 100% recordings linked to setup metadata and commit | Makes results auditable and application-ready. |

Targets are research objectives, not achieved claims. If a target is missed, record the result and iterate on sensor mounting, anti-aliasing, windowing, or threshold calibration rather than hiding it.

## Reproduce the synthetic benchmark

```bash
pip install -r requirements.txt
python analysis/train_demo.py --out docs/assets/condition-map.png --metrics docs/assets/demo_metrics.json
cat docs/assets/demo_metrics.json
```

The JSON file is ignored by Git because it is generated in CI/local validation; the plot is retained as a readable project preview.
