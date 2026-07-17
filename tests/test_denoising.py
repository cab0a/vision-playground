"""Tests for controlled denoising experiments."""

import csv
from pathlib import Path

import cv2
import numpy as np

from vision_playground.denoising import (
    generate_denoising_scenarios,
    run_denoising_experiment,
)


def test_noise_generation_is_deterministic() -> None:
    first = generate_denoising_scenarios(seed=5)
    second = generate_denoising_scenarios(seed=5)

    assert [scenario.noise_type for scenario in first] == [
        "gaussian",
        "salt_and_pepper",
    ]
    for first_scenario, second_scenario in zip(first, second, strict=True):
        assert np.array_equal(first_scenario.image, second_scenario.image)
        assert first_scenario.image.dtype == np.uint8


def test_denoising_experiment_writes_artifacts_and_improves_iou(
    tmp_path: Path,
) -> None:
    records = run_denoising_experiment(tmp_path)
    metrics_path = tmp_path / "denoising_metrics.csv"
    comparison_path = tmp_path / "denoising_comparison.png"

    assert len(records) == 6
    assert metrics_path.is_file()
    assert comparison_path.is_file()
    assert cv2.imread(str(comparison_path)) is not None

    with metrics_path.open(encoding="utf-8", newline="") as metrics_file:
        rows = list(csv.DictReader(metrics_file))
    assert len(rows) == 6

    scores = {
        (record.noise_type, record.denoising_method): record.iou
        for record in records
    }
    assert scores[("gaussian", "gaussian")] > scores[("gaussian", "none")]
    assert scores[("gaussian", "gaussian")] > scores[("gaussian", "median")]
    assert scores[("salt_and_pepper", "median")] > scores[
        ("salt_and_pepper", "none")
    ]
    assert scores[("salt_and_pepper", "median")] > scores[
        ("salt_and_pepper", "gaussian")
    ]
