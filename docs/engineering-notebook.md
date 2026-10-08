# Engineering notebook: turning raw signals into a health indicator

**Project:** InductiSense

**Author:** Ahmed Abdelrahman

**Revision:** 0.1 — 8 October 2026

## 1. Problem framing

A small induction motor often provides no early warning before a mechanical or electrical defect becomes costly. The question behind InductiSense is:

> Can a low-cost, isolated sensor node flag interpretable changes in motor current and vibration before a failure, while being honest about what the data can and cannot prove?

This is a **screening** problem, not a certified diagnosis problem. A useful first prototype must identify candidate signatures, retain raw evidence, and escalate to human inspection rather than promise that a single feature proves a fault.

## 2. Measurement choices

| Channel | Proposed sensor | Sample rate | What it contributes |
|---|---|---:|---|
| Motor current | Split-core CT + conditioned ADC | 4.096 kS/s | Electrical fundamental, harmonics, slip sidebands, RMS load context |
| Vibration | Digital 3-axis IMU | 1.6 kS/s | Rotational `1×/2×` components and high-frequency roughness energy |
| Context (future) | Temperature + voltage | 1–10 S/s | Helps distinguish load, cooling, and supply changes from a defect |

The CT clamps around **one insulated phase conductor**. Its physical isolation makes it preferable to an exposed voltage-divider prototype for an early student build. See [the wiring guide](../hardware/wiring.md) for the safety boundary.

## 3. Feature equations

Let a sampled current window be \(x[n]\), with \(N\) samples.

### RMS current

\[
I_{\mathrm{RMS}} = \sqrt{\frac{1}{N}\sum_{n=0}^{N-1} x[n]^2}
\]

RMS establishes load context. It should not be used alone as a fault label because it changes with the mechanical load.

### Crest factor

\[
CF = \frac{\max |x[n]|}{I_{\mathrm{RMS}}}
\]

A changing crest factor can reveal waveform distortion or clipping in the measurement chain. It is included primarily as a signal-quality and waveform-shape feature.

### Harmonic ratios

The Goertzel algorithm measures a narrow-band amplitude \(A(f)\) at a chosen frequency. The third- and fifth-harmonic ratios are:

\[
H_3 = \frac{A(3f_1)}{A(f_1)}, \qquad H_5 = \frac{A(5f_1)}{A(f_1)}
\]

This is computationally efficient on an MCU because only a few frequency components are needed; a full FFT is not required for each decision.

### Rotor-bar sideband ratio

For slip \(s\) and line frequency \(f_1\), a commonly investigated current-signature neighbourhood is:

\[
f_{SB} = f_1(1 \pm 2s)
\]

InductiSense uses an amplitude ratio rather than an absolute level:

\[
R_{SB} = \frac{A(f_1(1-2s)) + A(f_1(1+2s))}{2A(f_1)}
\]

The ratio reduces sensitivity to load-dependent overall current amplitude. It remains a **candidate indicator** because sideband content can be affected by supply unbalance, load oscillation, and sensor placement.

### Vibration indicators

With rotational frequency \(f_r\), the prototype calculates:

\[
R_{2\times} = \frac{A(2f_r)}{A(f_r)}
\]

and a high-frequency energy ratio:

\[
R_{HF} = \frac{\mathrm{RMS}\{X(f): 180 \leq f \leq 450\ \mathrm{Hz}\}}{\mathrm{RMS}\{x[n]\}}
\]

A high `2×` ratio is an alignment investigation cue; high-band energy is a bearing-roughness cue in this simplified prototype.

## 4. Edge decision logic

The portable firmware core evaluates transparent rules in `firmware/src/ConditionModel.cpp`:

1. high-frequency vibration dominates → **bearing-roughness signature**;
2. current sidebands exceed baseline trigger → **rotor-bar signature**;
3. `2×/1×` vibration ratio exceeds trigger → **misalignment signature**;
4. otherwise → **healthy / baseline-like**.

The output is intentionally labelled as a *signature* rather than a diagnosis. The associated number is a threshold margin—not a calibrated probability.

## 5. Sampling and resolution calculation

A 1-second window at 4,096 S/s contains 4,096 samples and produces a nominal 1 Hz FFT-bin spacing. A 50 Hz fundamental and illustrative 46/54 Hz slip sidebands therefore land near separate bins. In a physical build, frequency tracking or a longer window may be necessary when the mains frequency and slip drift.

For each test condition, record:

- motor nameplate data and load;
- line frequency and supply condition;
- CT range, orientation, and reference calibration;
- IMU mounting location and axis;
- sample rate, window length, and firmware commit;
- ambient temperature and the raw acquisition file.

## 6. Validation stance

The included Python data generator is **physics-inspired** and deliberately contains separable conditions. Its value is that it exercises the pipeline deterministically: generation → feature extraction → classifier → figure → unit tests. It does **not** establish diagnostic accuracy on a real motor.

The next meaningful experiment is a supervised lab campaign: capture a healthy baseline, introduce one safe and reversible perturbation under supervision (for example, a controlled alignment offset on a bench rig), and compare signatures against an independent vibration/reference instrument. Full proposed acceptance criteria appear in [validation.md](validation.md).
