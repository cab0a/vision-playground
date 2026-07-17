"""Tests for fixed and automatic thresholding methods."""

import numpy as np

from vision_playground.thresholding import (
    apply_fixed_threshold,
    apply_otsu_threshold,
)


def test_fixed_threshold_returns_a_binary_mask() -> None:
    image = np.array([[10, 127], [128, 240]], dtype=np.uint8)

    result = apply_fixed_threshold(image, threshold=127)

    assert result.method == "fixed"
    assert result.threshold == 127.0
    assert np.array_equal(
        result.mask,
        np.array([[0, 0], [255, 255]], dtype=np.uint8),
    )


def test_otsu_threshold_selects_between_two_intensity_groups() -> None:
    image = np.zeros((32, 32), dtype=np.uint8)
    image[:, 16:] = 200

    result = apply_otsu_threshold(image)

    assert result.method == "otsu"
    assert 0.0 <= result.threshold < 200.0
    assert set(np.unique(result.mask)) == {0, 255}
