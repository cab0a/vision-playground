"""Tests for adaptive parameter sensitivity artifacts."""

import csv
from pathlib import Path

import cv2

from vision_playground.sensitivity import run_adaptive_sensitivity


def test_sensitivity_experiment_writes_complete_grid(tmp_path: Path) -> None:
    output_dir = tmp_path / "results"

    records = run_adaptive_sensitivity(
        output_dir,
        block_sizes=(31, 63),
        c_values=(-10.0, 0.0),
    )

    metrics_path = output_dir / "adaptive_sensitivity_metrics.csv"
    heatmap_path = output_dir / "adaptive_sensitivity_heatmap.png"
    assert len(records) == 16
    assert metrics_path.is_file()
    assert heatmap_path.is_file()
    assert cv2.imread(str(heatmap_path)) is not None

    with metrics_path.open(encoding="utf-8", newline="") as metrics_file:
        rows = list(csv.DictReader(metrics_file))

    assert len(rows) == 16
    assert {row["block_size"] for row in rows} == {"31", "63"}
    assert {row["constant_c"] for row in rows} == {"-10.00", "0.00"}


def test_sensitivity_changes_across_image_conditions(tmp_path: Path) -> None:
    records = run_adaptive_sensitivity(
        tmp_path,
        block_sizes=(31, 191),
        c_values=(-10.0,),
    )
    scores = {
        (record.scenario, record.block_size): record.iou for record in records
    }

    assert scores[("uneven_illumination", 191)] > scores[
        ("uneven_illumination", 31)
    ]
