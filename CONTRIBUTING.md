# Contributing to InductiSense

Thanks for improving a learning-focused electrical-engineering project.

## Engineering principles

1. **Safety before novelty.** Do not add direct-mains build instructions or present the project as a protection device.
2. **Evidence labels matter.** Clearly label simulated results, bench results, and calibrated field results.
3. **Reproducibility is a feature.** Add or update a test for changes to the DSP or classifier.
4. **Keep decisions explainable.** A more complex classifier needs a benchmark and a documented reason it is better.
5. **Record the setup.** A physical dataset must include motor/load details, sensor placement, reference instrument, sampling configuration, and commit hash.

## Before opening a pull request

```bash
bash scripts/check.sh
```

Please describe the test conditions and whether a change affects hardware safety, feature definitions, thresholds, or validation claims.
