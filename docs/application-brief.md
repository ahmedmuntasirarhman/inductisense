# University application brief — InductiSense

**Applicant / author:** Ahmed Abdelrahman

**Project title:** *InductiSense: an edge-based health monitor for induction motors*

## 45-second project explanation

> I designed InductiSense to explore whether low-cost embedded sensing can flag early changes in induction motors before failure. I used a non-invasive current transformer and a vibration sensor, then built a signal-processing pipeline that calculates RMS current, harmonic ratios, rotor-bar sidebands, and vibration-band features. Instead of hiding the result inside a black box, I made the decision logic explainable and wrote reproducible tests around it. I also documented the safety boundary and a real-motor validation plan, because a simulation is not the same thing as a field result. The project combines the parts of electrical engineering I enjoy most: sensors, analogue interfaces, embedded code, and turning measurements into evidence.

## Technical highlights to discuss

| Topic | What to say | Evidence in repo |
| --- | --- | --- |
| Electrical measurement | “I chose a split-core CT to keep the first prototype electrically isolated from mains.” | `hardware/wiring.md`, `hardware/BOM.csv` |
| DSP | “I used RMS/crest-factor calculations and Goertzel detectors because they are lightweight enough for an MCU.” | `firmware/src/SignalFeatures.cpp`, `docs/engineering-notebook.md` |
| Motor theory | “I investigated sidebands around $$f_1(1\pm2s)$$, while treating them as indicators rather than proof of a rotor fault.” | `analysis/features.py`, engineering notebook |
| Mechanical systems | “A vibration IMU lets the system distinguish a strong 2× rotational component from high-frequency roughness.” | `analysis/synthetic_data.py` |
| Scientific honesty | “The current benchmark uses generated signals only; I distinguish that software test from physical measurements.” | `docs/validation.md` |
| Software quality | “The repository has Python tests, portable C++ tests, and CI so claims can be reproduced.” | `tests/`, `firmware/test/`, `.github/workflows/ci.yml` |

## Short application / CV description

**InductiSense — Independent Electrical Engineering Project (2026).** Designed a safe, edge-based motor-condition monitoring prototype using non-invasive current sensing and vibration analysis. Implemented portable C++ DSP for RMS, harmonic, and slip-sideband features; developed a reproducible Python benchmark and explainable classifier; authored a hardware BOM, safety-focused build guide, and physical validation protocol. *Author: Ahmed Abdelrahman.*

## Questions an interviewer might ask

### “Why not use a deep neural network?”

For an initial diagnostic tool, transparency and limited data matter. A feature-based baseline makes the relationship between a signal and an alert inspectable. Once measured, labelled data is available, a small quantised model could be compared against—not blindly replace—the explainable baseline.

### “What is the main weakness?”

The detector needs real data from the specific motor and load. Slip, supply variation, mounting position, and motor construction all affect the signatures. The project therefore calls its outputs screening indicators and proposes calibration/field validation before any strong reliability claim.

## Demonstrated project scope

The repository contains a reproducible synthetic-data pipeline, signal-feature extraction, a nearest-centroid demonstration, portable C++ DSP and rule-based decision code, regression tests, CI, a hardware reference design, and technical documentation. It does **not** contain a completed or measured physical prototype; the firmware's ADC/IMU integration remains a skeleton. Describe it as a software-validated prototype concept, not as a field-tested motor diagnostic system.
