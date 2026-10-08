#include "SignalFeatures.h"

#include <algorithm>
#include <cmath>

namespace inductisense {
namespace {
constexpr float kPi = 3.14159265358979323846F;
}

float calculateRms(const float* samples, std::size_t count) {
  if (samples == nullptr || count == 0) return 0.0F;
  float energy = 0.0F;
  for (std::size_t index = 0; index < count; ++index) {
    energy += samples[index] * samples[index];
  }
  return std::sqrt(energy / static_cast<float>(count));
}

float calculateCrestFactor(const float* samples, std::size_t count) {
  if (samples == nullptr || count == 0) return 0.0F;
  float peak = 0.0F;
  for (std::size_t index = 0; index < count; ++index) {
    peak = std::max(peak, std::fabs(samples[index]));
  }
  const float rms = calculateRms(samples, count);
  return rms > 1e-9F ? peak / rms : 0.0F;
}

float goertzelAmplitude(const float* samples, std::size_t count,
                        float sample_rate_hz, float target_hz) {
  if (samples == nullptr || count < 2 || sample_rate_hz <= 0.0F ||
      target_hz <= 0.0F || target_hz >= sample_rate_hz * 0.5F) {
    return 0.0F;
  }

  // Remove DC before a narrow-band amplitude estimate.
  float mean = 0.0F;
  for (std::size_t index = 0; index < count; ++index) mean += samples[index];
  mean /= static_cast<float>(count);

  const float omega = 2.0F * kPi * target_hz / sample_rate_hz;
  const float coefficient = 2.0F * std::cos(omega);
  float previous = 0.0F;
  float previous_previous = 0.0F;
  for (std::size_t index = 0; index < count; ++index) {
    const float current = samples[index] - mean + coefficient * previous - previous_previous;
    previous_previous = previous;
    previous = current;
  }
  const float real = previous - previous_previous * std::cos(omega);
  const float imaginary = previous_previous * std::sin(omega);
  return 2.0F * std::sqrt(real * real + imaginary * imaginary) /
         static_cast<float>(count);
}

float calculateSidebandRatio(const float* current_samples, std::size_t count,
                             float sample_rate_hz, float line_frequency_hz,
                             float slip) {
  if (slip <= 0.0F || slip >= 0.5F) return 0.0F;
  const float fundamental = goertzelAmplitude(
      current_samples, count, sample_rate_hz, line_frequency_hz);
  if (fundamental < 1e-9F) return 0.0F;
  const float offset = 2.0F * slip * line_frequency_hz;
  const float lower = goertzelAmplitude(
      current_samples, count, sample_rate_hz, line_frequency_hz - offset);
  const float upper = goertzelAmplitude(
      current_samples, count, sample_rate_hz, line_frequency_hz + offset);
  return 0.5F * (lower + upper) / fundamental;
}

CurrentFeatures extractCurrentFeatures(const float* current_samples,
                                       std::size_t count,
                                       float sample_rate_hz,
                                       float line_frequency_hz,
                                       float slip) {
  const float fundamental = std::max(
      goertzelAmplitude(current_samples, count, sample_rate_hz, line_frequency_hz),
      1e-9F);
  return {
      calculateRms(current_samples, count),
      calculateCrestFactor(current_samples, count),
      goertzelAmplitude(current_samples, count, sample_rate_hz,
                        3.0F * line_frequency_hz) /
          fundamental,
      goertzelAmplitude(current_samples, count, sample_rate_hz,
                        5.0F * line_frequency_hz) /
          fundamental,
      calculateSidebandRatio(current_samples, count, sample_rate_hz,
                             line_frequency_hz, slip),
  };
}

}  // namespace inductisense
