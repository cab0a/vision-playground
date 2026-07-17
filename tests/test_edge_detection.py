"""Tests for controlled edge detection."""

import csv
from pathlib import Path

import cv2
import numpy as np

from vision_playground.edge_detection import (
    calculate_edge_metrics,
    run_edge_experiment,
)


def test_edge_metrics_allow_small_positional_error() -> None:
    ground_truth = np.zeros((32, 32), dtype=np.uint8)
    prediction = np.zeros_like(ground_truth)
    ground_truth[:, 15] = 255
    prediction[:, 16] = 255

    exact = calculate_edge_metrics(prediction, ground_truth, tolerance_pixels=0)
    tolerant = calculate_edge_metrics(
        prediction,
        ground_truth,
        tolerance_pixels=1,
    )

    assert exact.f1 == 0.0
    assert tolerant.f1 == 1.0


def test_edge_experiment_writes_artifacts_and_tracks_noise(
    tmp_path: Path,
) -> None:
    records = run_edge_experiment(tmp_path)
    metrics_path = tmp_path / "edge_detection_metrics.csv"
    comparison_path = tmp_path / "edge_detection_comparison.png"

    assert len(records) == 9
    assert metrics_path.is_file()
    assert comparison_path.is_file()
    assert cv2.imread(str(comparison_path)) is not None

    with metrics_path.open(encoding="utf-8", newline="") as metrics_file:
        rows = list(csv.DictReader(metrics_file))
    assert len(rows) == 9

    scores = {
        (record.condition, record.denoising_method): record.f1
        for record in records
    }
    assert scores[("clean", "none")] == 1.0
    assert scores[("gaussian", "gaussian")] > scores[("gaussian", "none")]
    assert scores[("salt_and_pepper", "median")] > scores[
        ("salt_and_pepper", "gaussian")
    ]
