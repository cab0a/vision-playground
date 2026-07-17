"""Tests for public-image denoising stability artifacts."""

from pathlib import Path

import cv2
import numpy as np

from vision_playground.denoising_sample import evaluate_denoising_samples


def test_denoising_sample_writes_summary_and_comparison(
    tmp_path: Path,
) -> None:
    image_path = tmp_path / "sample.png"
    image = np.tile(np.arange(128, dtype=np.uint8), (128, 1))
    assert cv2.imwrite(str(image_path), image)

    output_dir = tmp_path / "results"
    records = evaluate_denoising_samples([image_path], output_dir)

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
    assert (output_dir / "denoising_summary.csv").is_file()
    comparison_path = output_dir / "denoising_comparison.jpg"
    assert comparison_path.is_file()
    assert cv2.imread(str(comparison_path)) is not None
