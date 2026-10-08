import unittest

import numpy as np

from analysis.features import extract_features
from analysis.synthetic_data import generate_sample
from analysis.train_demo import build_dataset, evaluate


class FeatureExtractionTests(unittest.TestCase):
    def test_rotor_bar_sidebands_exceed_healthy_baseline(self):
        healthy_current, healthy_vibration = generate_sample("healthy", seed=21)
        fault_current, fault_vibration = generate_sample("rotor_bar", seed=21)
        healthy = extract_features(healthy_current, healthy_vibration)
        rotor_bar = extract_features(fault_current, fault_vibration)
        self.assertGreater(rotor_bar.sideband_ratio, healthy.sideband_ratio * 3.0)

    def test_misalignment_has_dominant_2x_vibration(self):
        current, vibration = generate_sample("misalignment", seed=9)
        features = extract_features(current, vibration)
        self.assertGreater(features.vibration_2x_to_1x, 1.25)

    def test_bearing_roughness_has_higher_high_frequency_energy(self):
        healthy_current, healthy_vibration = generate_sample("healthy", seed=7)
        bearing_current, bearing_vibration = generate_sample("bearing_roughness", seed=7)
        healthy = extract_features(healthy_current, healthy_vibration)
        bearing = extract_features(bearing_current, bearing_vibration)
        self.assertGreater(bearing.high_frequency_ratio, healthy.high_frequency_ratio * 4.0)

    def test_demo_is_reproducible_and_separable(self):
        features, labels = build_dataset(examples_per_class=120)
        metrics = evaluate(features, labels)
        self.assertEqual(features.shape, (480, 9))
        self.assertEqual(labels.shape, (480,))
        self.assertGreaterEqual(metrics["accuracy"], 0.95)
        self.assertTrue(np.isfinite(features).all())


if __name__ == "__main__":
    unittest.main()
