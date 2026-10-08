#pragma once

namespace inductisense {

enum class HealthState {
  kHealthy,
  kRotorBarIndicator,
  kMisalignmentIndicator,
  kBearingRoughnessIndicator,
};

struct MechanicalFeatures {
  float vibration_1x;
  float vibration_2x;
  float high_frequency_ratio;
};

struct Decision {
  HealthState state;
  float confidence;  // Rule-margin score in [0, 1], not a calibrated probability.
};

/**
 * Apply transparent screening rules. Alarm states identify a signature to
 * investigate; they are never a final maintenance diagnosis.
 */
Decision classifyHealth(float sideband_ratio,
                        const MechanicalFeatures& mechanical_features);

const char* healthStateName(HealthState state);

}  // namespace inductisense
