"""Physics-inspired, labelled signals for repeatable pipeline validation.

These models are deliberately simplified. They are useful for exercising the DSP
and classifier before collecting real machine data, not for claiming field accuracy.
"""
from __future__ import annotations

from typing import Tuple

import numpy as np

LABELS = ("healthy", "rotor_bar", "misalignment", "bearing_roughness")


def generate_sample(label: str, seed: int, duration_s: float = 1.0) -> Tuple[np.ndarray, np.ndarray]:
    """Generate a current/vibration pair for one operating state."""
    if label not in LABELS:
        raise ValueError(f"Unknown label: {label}")
    rng = np.random.default_rng(seed)
    current_rate, vibration_rate = 4096.0, 1600.0
    current_time = np.arange(int(current_rate * duration_s)) / current_rate
    vibration_time = np.arange(int(vibration_rate * duration_s)) / vibration_rate

    line_hz = 50.0 + rng.normal(0.0, 0.05)
    rotor_hz = 25.0 + rng.normal(0.0, 0.10)
    current_amplitude = 1.0 + rng.normal(0.0, 0.035)

    # Fundamental current with ordinary magnetising harmonics.
    current = current_amplitude * np.sin(2.0 * np.pi * line_hz * current_time)
    current += (0.018 + rng.uniform(0.0, 0.006)) * np.sin(2.0 * np.pi * 3.0 * line_hz * current_time)
    current += (0.012 + rng.uniform(0.0, 0.006)) * np.sin(2.0 * np.pi * 5.0 * line_hz * current_time)
    current += rng.normal(0.0, 0.008, current_time.size)

    # A normal motor has a modest 1x rotational vibration component.
    vibration = 0.18 * np.sin(2.0 * np.pi * rotor_hz * vibration_time)
    vibration += rng.normal(0.0, 0.018, vibration_time.size)

    if label == "rotor_bar":
        # MCSA sidebands occur around f1 ± 2*s*f1. Slip is approximately 0.04.
        for frequency in (line_hz * 0.92, line_hz * 1.08):
            current += (0.095 + rng.uniform(0.0, 0.025)) * np.sin(2.0 * np.pi * frequency * current_time)
        vibration += 0.04 * np.sin(2.0 * np.pi * 2.0 * rotor_hz * vibration_time)
    elif label == "misalignment":
        vibration += (0.34 + rng.uniform(0.0, 0.06)) * np.sin(2.0 * np.pi * 2.0 * rotor_hz * vibration_time)
        current += 0.035 * np.sin(2.0 * np.pi * 5.0 * line_hz * current_time)
    elif label == "bearing_roughness":
        # High-frequency, amplitude-modulated vibration is a simplified bearing cue.
        carrier = np.sin(2.0 * np.pi * 260.0 * vibration_time)
        envelope = 0.4 + 0.6 * np.sin(2.0 * np.pi * rotor_hz * vibration_time) ** 2
        vibration += (0.20 + rng.uniform(0.0, 0.04)) * envelope * carrier
        vibration += rng.normal(0.0, 0.035, vibration_time.size)

    return current, vibration
