"""Tests for public-image edge stability artifacts."""

from pathlib import Path

import cv2
import numpy as np

from vision_playground.edge_sample import evaluate_edge_samples


def test_edge_sample_writes_summary_and_comparison(tmp_path: Path) -> None:
    image_path = tmp_path / "sample.png"
    image = np.zeros((128, 128), dtype=np.uint8)
    cv2.rectangle(image, (24, 24), (104, 104), 200, thickness=-1)
    assert cv2.imwrite(str(image_path), image)

    output_dir = tmp_path / "results"
    records = evaluate_edge_samples([image_path], output_dir)

    assert len(records) == 6
    assert {record.noise_type for record in records} == {
        "gaussian",
        "salt_and_pepper",
    }
    assert {record.denoising_method for record in records} == {
        "none",
        "gaussian",
        "median",
    }
    assert (output_dir / "edge_detection_summary.csv").is_file()
    comparison_path = output_dir / "edge_detection_comparison.jpg"
    assert comparison_path.is_file()
    assert cv2.imread(str(comparison_path)) is not None
