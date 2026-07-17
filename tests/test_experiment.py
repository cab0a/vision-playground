"""Tests for experiment artifact generation."""

import csv
from pathlib import Path

import cv2

from vision_playground.experiment import run_thresholding_experiment


def test_experiment_writes_metrics_and_comparison(tmp_path: Path) -> None:
    output_dir = tmp_path / "results"

    records = run_thresholding_experiment(output_dir)

    metrics_path = output_dir / "thresholding_metrics.csv"
    comparison_path = output_dir / "thresholding_comparison.png"
    assert len(records) == 12
    assert metrics_path.is_file()
    assert comparison_path.is_file()
    assert cv2.imread(str(comparison_path)) is not None

    with metrics_path.open(encoding="utf-8", newline="") as metrics_file:
        rows = list(csv.DictReader(metrics_file))

    assert len(rows) == 12
    assert {row["method"] for row in rows} == {"fixed", "otsu", "adaptive"}
    adaptive_rows = [row for row in rows if row["method"] == "adaptive"]
    assert all(row["threshold"] == "" for row in adaptive_rows)
    assert all(row["block_size"] == "127" for row in adaptive_rows)
    assert all(row["constant_c"] == "-10.00" for row in adaptive_rows)

    uneven_records = {
        record.method: record
        for record in records
        if record.scenario == "uneven_illumination"
    }
    assert uneven_records["adaptive"].iou > uneven_records["fixed"].iou
    assert uneven_records["adaptive"].iou > uneven_records["otsu"].iou
