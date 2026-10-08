#include <Arduino.h>

#include "ConditionModel.h"
#include "SignalFeatures.h"

namespace {
constexpr int kCurrentInputPin = 4;  // AFE output; adjust after PCB/wiring validation.
constexpr int kSamplesPerWindow = 1024;
constexpr float kSampleRateHz = 4096.0F;
constexpr float kLineFrequencyHz = 50.0F;
constexpr float kEstimatedSlip = 0.04F;
float current_window[kSamplesPerWindow];

// Placeholder until the ADS131M02 SPI driver is integrated. This permits
// bench testing with a low-voltage, biased analogue signal only.
float readCurrentSample() {
  const float millivolts = static_cast<float>(analogReadMilliVolts(kCurrentInputPin));
  return (millivolts - 1650.0F) / 1000.0F;
}

void captureWindow() {
  const uint32_t interval_us = static_cast<uint32_t>(1'000'000.0F / kSampleRateHz);
  uint32_t next_sample_us = micros();
  for (int index = 0; index < kSamplesPerWindow; ++index) {
    while (static_cast<int32_t>(micros() - next_sample_us) < 0) {
      // Intentional busy wait: replace with DMA/timer acquisition for field use.
    }
    current_window[index] = readCurrentSample();
    next_sample_us += interval_us;
  }
}
}  // namespace

void setup() {
  Serial.begin(115200);
  analogReadResolution(12);
  Serial.println("InductiSense prototype booted. Use isolated low-voltage signals only.");
}

void loop() {
  captureWindow();
  const auto current = inductisense::extractCurrentFeatures(
      current_window, kSamplesPerWindow, kSampleRateHz, kLineFrequencyHz,
      kEstimatedSlip);

  // Replace with real IMU features once an ICM-42688/ADXL345 driver is connected.
  const inductisense::MechanicalFeatures mechanical{0.18F, 0.10F, 0.05F};
  const auto decision = inductisense::classifyHealth(current.sideband_ratio, mechanical);

  Serial.printf("rms=%.3f, crest=%.2f, sideband=%.3f, state=%s, rule-margin=%.2f\n",
                current.rms, current.crest_factor, current.sideband_ratio,
                inductisense::healthStateName(decision.state), decision.confidence);
  delay(750);
}
