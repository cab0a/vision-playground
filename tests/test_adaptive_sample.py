"""Tests for qualitative adaptive public-sample artifacts."""

from pathlib import Path

import cv2
import numpy as np

from vision_playground.adaptive_sample import (
    AdaptiveConfiguration,
    evaluate_adaptive_samples,
)


def test_adaptive_sample_writes_summary_and_comparison(tmp_path: Path) -> None:
    image_path = tmp_path / "sample.png"
    image = np.tile(np.arange(96, dtype=np.uint8), (96, 1))
    assert cv2.imwrite(str(image_path), image)

    output_dir = tmp_path / "results"
    configurations = (
        AdaptiveConfiguration("small", 15, 2.0),
        AdaptiveConfiguration("large", 63, -5.0),
    )
    records = evaluate_adaptive_samples(
        [image_path],
        output_dir,
        configurations=configurations,
    )

    assert len(records) == 2
    assert {record.configuration for record in records} == {"small", "large"}
    assert (output_dir / "adaptive_parameter_summary.csv").is_file()
    comparison_path = output_dir / "adaptive_parameter_comparison.jpg"
    assert comparison_path.is_file()
    assert cv2.imread(str(comparison_path)) is not None
