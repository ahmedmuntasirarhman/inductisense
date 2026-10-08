"""Explainable signal features used by the InductiSense benchmark.

The functions intentionally use direct FFT-bin measurements rather than a black-box
model so that every health decision can be traced to a physical signal property.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import numpy as np


@dataclass(frozen=True)
class MotorFeatures:
    """Feature vector with a stable ordering for the demo classifier."""

    current_rms: float
    current_crest: float
    third_harmonic_ratio: float
    fifth_harmonic_ratio: float
    sideband_ratio: float
    vibration_rms: float
    vibration_2x_to_1x: float
    high_frequency_ratio: float
    kurtosis: float

    def as_array(self) -> np.ndarray:
        return np.asarray([
            self.current_rms,
            self.current_crest,
            self.third_harmonic_ratio,
            self.fifth_harmonic_ratio,
            self.sideband_ratio,
            self.vibration_rms,
            self.vibration_2x_to_1x,
            self.high_frequency_ratio,
            self.kurtosis,
        ], dtype=float)


def _amplitude_at(signal: np.ndarray, sample_rate: float, target_hz: float) -> float:
    """Return single-sided FFT amplitude nearest *target_hz* after mean removal."""
    centered = np.asarray(signal, dtype=float) - np.mean(signal)
    spectrum = np.fft.rfft(centered)
    frequencies = np.fft.rfftfreq(centered.size, d=1.0 / sample_rate)
    index = int(np.argmin(np.abs(frequencies - target_hz)))
    return float(2.0 * np.abs(spectrum[index]) / centered.size)


def _band_rms(signal: np.ndarray, sample_rate: float, low_hz: float, high_hz: float) -> float:
    """Estimate RMS energy contained in an FFT band, excluding DC."""
    centered = np.asarray(signal, dtype=float) - np.mean(signal)
    spectrum = np.fft.rfft(centered)
    frequencies = np.fft.rfftfreq(centered.size, d=1.0 / sample_rate)
    keep = (frequencies >= low_hz) & (frequencies <= high_hz)
    if not np.any(keep):
        return 0.0
    # Parseval-scaled approximation for a real, one-sided spectrum.
    power = np.sum(np.abs(spectrum[keep]) ** 2) * 2.0 / (centered.size**2)
    return float(np.sqrt(max(power, 0.0)))


def extract_features(
    current: Iterable[float],
    vibration: Iterable[float],
    current_sample_rate: float = 4096.0,
    vibration_sample_rate: float = 1600.0,
    line_frequency: float = 50.0,
    slip: float = 0.04,
) -> MotorFeatures:
    """Extract transparent current-signature and vibration features.

    The sideband ratio measures average amplitude near ``f1 ± 2*s*f1`` against
    the fundamental. A high value is a screening flag for a rotor-bar anomaly.
    """
    current_array = np.asarray(list(current), dtype=float)
    vibration_array = np.asarray(list(vibration), dtype=float)
    if current_array.size < 64 or vibration_array.size < 64:
        raise ValueError("At least 64 samples are required for each channel.")

    fundamental = max(_amplitude_at(current_array, current_sample_rate, line_frequency), 1e-12)
    lower_sideband = _amplitude_at(current_array, current_sample_rate, line_frequency * (1.0 - 2.0 * slip))
    upper_sideband = _amplitude_at(current_array, current_sample_rate, line_frequency * (1.0 + 2.0 * slip))
    current_rms = float(np.sqrt(np.mean(np.square(current_array))))
    peak = float(np.max(np.abs(current_array)))
    vibration_rms = float(np.sqrt(np.mean(np.square(vibration_array))))
    vibration_1x = max(_amplitude_at(vibration_array, vibration_sample_rate, 25.0), 1e-12)
    vibration_2x = _amplitude_at(vibration_array, vibration_sample_rate, 50.0)
    centered_vibration = vibration_array - np.mean(vibration_array)
    variance = float(np.mean(centered_vibration**2))
    kurtosis = float(np.mean(centered_vibration**4) / max(variance**2, 1e-12))

    return MotorFeatures(
        current_rms=current_rms,
        current_crest=peak / max(current_rms, 1e-12),
        third_harmonic_ratio=_amplitude_at(current_array, current_sample_rate, 3.0 * line_frequency) / fundamental,
        fifth_harmonic_ratio=_amplitude_at(current_array, current_sample_rate, 5.0 * line_frequency) / fundamental,
        sideband_ratio=0.5 * (lower_sideband + upper_sideband) / fundamental,
        vibration_rms=vibration_rms,
        vibration_2x_to_1x=vibration_2x / vibration_1x,
        high_frequency_ratio=_band_rms(vibration_array, vibration_sample_rate, 180.0, 450.0) / max(vibration_rms, 1e-12),
        kurtosis=kurtosis,
    )
