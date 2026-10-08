#!/usr/bin/env python3
"""Train and evaluate an explainable nearest-centroid health classifier.

Usage:
    python analysis/train_demo.py --out docs/assets/condition-map.png \
        --metrics docs/assets/demo_metrics.json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, Tuple

import matplotlib.pyplot as plt
import numpy as np

# Permit both ``python -m analysis.train_demo`` and direct script execution.
if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from analysis.features import extract_features
from analysis.synthetic_data import LABELS, generate_sample


def build_dataset(examples_per_class: int = 120) -> Tuple[np.ndarray, np.ndarray]:
    rows, labels = [], []
    for label_index, label in enumerate(LABELS):
        for sample_index in range(examples_per_class):
            current, vibration = generate_sample(label, seed=10_000 * label_index + sample_index)
            rows.append(extract_features(current, vibration).as_array())
            labels.append(label)
    return np.asarray(rows), np.asarray(labels)


def evaluate(features: np.ndarray, labels: np.ndarray) -> Dict[str, object]:
    """Perform a deterministic stratified holdout test with a centroid classifier."""
    train_indices, test_indices = [], []
    for label in LABELS:
        indices = np.flatnonzero(labels == label)
        train_indices.extend(indices[:80])
        test_indices.extend(indices[80:])
    train_indices, test_indices = np.asarray(train_indices), np.asarray(test_indices)
    train_x, test_x = features[train_indices], features[test_indices]
    train_y, test_y = labels[train_indices], labels[test_indices]

    mean = train_x.mean(axis=0)
    std = np.maximum(train_x.std(axis=0), 1e-9)
    train_z, test_z = (train_x - mean) / std, (test_x - mean) / std
    centroids = np.stack([train_z[train_y == label].mean(axis=0) for label in LABELS])
    distances = ((test_z[:, None, :] - centroids[None, :, :]) ** 2).sum(axis=2)
    predicted = np.asarray(LABELS)[np.argmin(distances, axis=1)]
    accuracy = float(np.mean(predicted == test_y))

    confusion = {
        actual: {predicted_label: int(np.sum((test_y == actual) & (predicted == predicted_label))) for predicted_label in LABELS}
        for actual in LABELS
    }
    return {
        "accuracy": accuracy,
        "examples_per_class": 120,
        "holdout_examples_per_class": 40,
        "feature_count": int(features.shape[1]),
        "labels": list(LABELS),
        "confusion_matrix": confusion,
        "normalisation": "z-score based on training partition only",
    }


def plot_feature_map(features: np.ndarray, labels: np.ndarray, output: Path) -> None:
    """Plot two principal components of standardised, labelled feature vectors."""
    z = (features - features.mean(axis=0)) / np.maximum(features.std(axis=0), 1e-9)
    _, _, right_vectors = np.linalg.svd(z, full_matrices=False)
    projected = z @ right_vectors[:2].T
    colours = {"healthy": "#16a34a", "rotor_bar": "#dc2626", "misalignment": "#2563eb", "bearing_roughness": "#9333ea"}

    plt.style.use("seaborn-v0_8-whitegrid")
    figure, axis = plt.subplots(figsize=(9, 5.4), dpi=180)
    for label in LABELS:
        selected = labels == label
        axis.scatter(projected[selected, 0], projected[selected, 1], s=18, alpha=0.72, label=label.replace("_", " "), color=colours[label], edgecolors="none")
    axis.set_title("InductiSense synthetic benchmark: feature-space separation", weight="bold")
    axis.set_xlabel("Principal component 1")
    axis.set_ylabel("Principal component 2")
    axis.legend(title="Modelled state", frameon=True)
    axis.text(0.01, -0.16, "Synthetic, physics-inspired signals — not field-performance evidence.", transform=axis.transAxes, fontsize=8, color="#475569")
    figure.tight_layout()
    output.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(output, bbox_inches="tight")
    plt.close(figure)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=Path("docs/assets/condition-map.png"))
    parser.add_argument("--metrics", type=Path, default=Path("docs/assets/demo_metrics.json"))
    arguments = parser.parse_args()

    features, labels = build_dataset()
    metrics = evaluate(features, labels)
    plot_feature_map(features, labels, arguments.out)
    arguments.metrics.parent.mkdir(parents=True, exist_ok=True)
    arguments.metrics.write_text(json.dumps(metrics, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()
