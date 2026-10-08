#include "ConditionModel.h"

#include <algorithm>

namespace inductisense {
namespace {
float clamp01(float value) { return std::max(0.0F, std::min(1.0F, value)); }
}

Decision classifyHealth(float sideband_ratio,
                        const MechanicalFeatures& mechanical_features) {
  // Thresholds are initial investigation triggers derived from the project's
  // synthetic benchmark. They must be calibrated against a target motor.
  if (mechanical_features.high_frequency_ratio > 0.28F) {
    return {HealthState::kBearingRoughnessIndicator,
            clamp01((mechanical_features.high_frequency_ratio - 0.28F) / 0.45F)};
  }
  if (sideband_ratio > 0.070F) {
    return {HealthState::kRotorBarIndicator,
            clamp01((sideband_ratio - 0.070F) / 0.12F)};
  }
  const float one_x = std::max(mechanical_features.vibration_1x, 1e-6F);
  const float ratio_2x_to_1x = mechanical_features.vibration_2x / one_x;
  if (ratio_2x_to_1x > 1.25F) {
    return {HealthState::kMisalignmentIndicator,
            clamp01((ratio_2x_to_1x - 1.25F) / 2.0F)};
  }
  return {HealthState::kHealthy, 1.0F - clamp01(sideband_ratio / 0.070F)};
}

const char* healthStateName(HealthState state) {
  switch (state) {
    case HealthState::kHealthy:
      return "healthy";
    case HealthState::kRotorBarIndicator:
      return "rotor-bar signature";
    case HealthState::kMisalignmentIndicator:
      return "misalignment signature";
    case HealthState::kBearingRoughnessIndicator:
      return "bearing-roughness signature";
  }
  return "unknown";
}

}  // namespace inductisense
