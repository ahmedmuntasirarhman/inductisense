#include <cassert>
#include <cmath>
#include <iostream>
#include <vector>

#include "ConditionModel.h"
#include "SignalFeatures.h"

namespace {
constexpr float kPi = 3.14159265358979323846F;

std::vector<float> sine(float frequency, float amplitude, float sample_rate,
                        int sample_count) {
  std::vector<float> values(sample_count);
  for (int index = 0; index < sample_count; ++index) {
    values[index] = amplitude * std::sin(2.0F * kPi * frequency *
                                         static_cast<float>(index) / sample_rate);
  }
  return values;
}

bool close(float actual, float expected, float tolerance) {
  return std::fabs(actual - expected) <= tolerance;
}
}  // namespace

int main() {
  constexpr float kSampleRate = 1000.0F;
  auto current = sine(50.0F, 2.0F, kSampleRate, 2000);
  assert(close(inductisense::calculateRms(current.data(), current.size()),
               std::sqrt(2.0F), 0.01F));
  assert(close(inductisense::calculateCrestFactor(current.data(), current.size()),
               std::sqrt(2.0F), 0.02F));
  assert(close(inductisense::goertzelAmplitude(current.data(), current.size(),
                                                 kSampleRate, 50.0F),
               2.0F, 0.02F));

  auto sideband_current = current;
  auto low = sine(46.0F, 0.10F, kSampleRate, 2000);
  auto high = sine(54.0F, 0.10F, kSampleRate, 2000);
  for (std::size_t index = 0; index < sideband_current.size(); ++index) {
    sideband_current[index] += low[index] + high[index];
  }
  const float sideband_ratio = inductisense::calculateSidebandRatio(
      sideband_current.data(), sideband_current.size(), kSampleRate, 50.0F, 0.04F);
  assert(close(sideband_ratio, 0.05F, 0.01F));

  using inductisense::HealthState;
  assert(inductisense::classifyHealth(0.12F, {0.2F, 0.1F, 0.05F}).state ==
         HealthState::kRotorBarIndicator);
  assert(inductisense::classifyHealth(0.01F, {0.2F, 0.4F, 0.05F}).state ==
         HealthState::kMisalignmentIndicator);
  assert(inductisense::classifyHealth(0.01F, {0.2F, 0.1F, 0.55F}).state ==
         HealthState::kBearingRoughnessIndicator);

  std::cout << "All firmware-core tests passed.\n";
  return 0;
}
