#pragma once

#include <cstddef>

namespace inductisense {

struct CurrentFeatures {
  float rms;
  float crest_factor;
  float third_harmonic_ratio;
  float fifth_harmonic_ratio;
  float sideband_ratio;
};

float calculateRms(const float* samples, std::size_t count);
float calculateCrestFactor(const float* samples, std::size_t count);

/**
 * Estimate the peak amplitude at a target frequency using a Goertzel detector.
 * The result is amplitude (not RMS), provided target_hz aligns closely with an
 * FFT bin over the measurement window.
 */
float goertzelAmplitude(const float* samples, std::size_t count,
                        float sample_rate_hz, float target_hz);

float calculateSidebandRatio(const float* current_samples, std::size_t count,
                             float sample_rate_hz, float line_frequency_hz,
                             float slip);

CurrentFeatures extractCurrentFeatures(const float* current_samples,
                                       std::size_t count,
                                       float sample_rate_hz,
                                       float line_frequency_hz,
                                       float slip);

}  // namespace inductisense
