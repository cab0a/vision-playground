"""Tests for qualitative real-image artifact generation."""

from pathlib import Path

import cv2
import numpy as np

from vision_playground.real_images import evaluate_real_images


def test_real_image_evaluation_writes_summary_and_comparison(
    tmp_path: Path,
) -> None:
    image_path = tmp_path / "sample.png"
    image = np.zeros((48, 64), dtype=np.uint8)
    image[:, 32:] = 200
    assert cv2.imwrite(str(image_path), image)

    output_dir = tmp_path / "results"
    records = evaluate_real_images([image_path], output_dir)

    assert len(records) == 2
    assert {record.method for record in records} == {"fixed", "otsu"}
    assert (output_dir / "thresholding_summary.csv").is_file()
    assert (output_dir / "thresholding_comparison.jpg").is_file()
