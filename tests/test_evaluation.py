"""Tests for binary segmentation metrics."""

import numpy as np
import pytest

from vision_playground.evaluation import calculate_binary_metrics


def test_identical_masks_receive_perfect_scores() -> None:
    mask = np.array([[0, 255], [255, 0]], dtype=np.uint8)

    metrics = calculate_binary_metrics(mask, mask)

    assert metrics.iou == pytest.approx(1.0)
    assert metrics.precision == pytest.approx(1.0)
    assert metrics.recall == pytest.approx(1.0)
    assert metrics.f1 == pytest.approx(1.0)


def test_partial_overlap_produces_expected_scores() -> None:
    predicted = np.array([[255, 255], [0, 0]], dtype=np.uint8)
    ground_truth = np.array([[255, 0], [255, 0]], dtype=np.uint8)

    metrics = calculate_binary_metrics(predicted, ground_truth)

    assert metrics.iou == pytest.approx(1 / 3)
    assert metrics.precision == pytest.approx(0.5)
    assert metrics.recall == pytest.approx(0.5)
    assert metrics.f1 == pytest.approx(0.5)
