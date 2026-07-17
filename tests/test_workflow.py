"""Tests for the inspected vision workflow."""

import csv
from pathlib import Path

import cv2
import numpy as np

from vision_playground.workflow import run_inspected_workflow


def test_workflow_inspects_inputs_and_evaluates_only_valid_images(
    tmp_path: Path,
) -> None:
    images_dir = tmp_path / "images"
    images_dir.mkdir()

    valid_path = images_dir / "valid.png"
    image = np.zeros((48, 64), dtype=np.uint8)
    image[:, 32:] = 200
    assert cv2.imwrite(str(valid_path), image)
    (images_dir / "broken.jpg").write_bytes(b"not an image")

    output_dir = tmp_path / "results"
    inspections, workflow_records = run_inspected_workflow(
        images_dir,
        output_dir,
    )

    assert len(inspections) == 2
    assert {result.status for result in inspections} == {"valid", "unreadable"}
    assert len(workflow_records) == 1
    assert workflow_records[0].relative_path == "valid.png"
    assert workflow_records[0].foreground_fraction_delta >= 0.0

    expected_outputs = (
        "input_inspection.csv",
        "thresholding_summary.csv",
        "thresholding_comparison.jpg",
        "workflow_summary.csv",
    )
    assert all((output_dir / name).is_file() for name in expected_outputs)

    with (output_dir / "workflow_summary.csv").open(
        encoding="utf-8",
        newline="",
    ) as summary_file:
        rows = list(csv.DictReader(summary_file))

    assert len(rows) == 1
    assert rows[0]["relative_path"] == "valid.png"
