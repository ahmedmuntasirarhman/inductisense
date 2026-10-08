#!/usr/bin/env bash
set -euo pipefail

python3 -m unittest discover -s tests -v
python3 analysis/train_demo.py --out docs/assets/condition-map.png --metrics /tmp/inductisense_metrics.json
g++ -std=c++17 -Wall -Wextra -pedantic -Ifirmware/include \
  firmware/src/SignalFeatures.cpp firmware/src/ConditionModel.cpp \
  firmware/test/test_signal_features.cpp -o /tmp/inductisense_firmware_test
/tmp/inductisense_firmware_test
printf '\nValidation complete. Metrics: /tmp/inductisense_metrics.json\n'
