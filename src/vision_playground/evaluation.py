"""Binary segmentation metrics for thresholding experiments."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True, slots=True)
class BinaryMetrics:
    """Pixel-level metrics for one predicted binary mask."""

    iou: float
    precision: float
    recall: float
    f1: float


def calculate_binary_metrics(
    predicted: np.ndarray,
    ground_truth: np.ndarray,
) -> BinaryMetrics:
    """Compare two same-shaped masks using nonzero pixels as foreground."""
    if predicted.shape != ground_truth.shape:
        raise ValueError("Predicted and ground-truth masks must have the same shape.")

    predicted_foreground = predicted != 0
    ground_truth_foreground = ground_truth != 0

    true_positive = int(
        np.count_nonzero(predicted_foreground & ground_truth_foreground)
    )
    false_positive = int(
        np.count_nonzero(predicted_foreground & ~ground_truth_foreground)
    )
    false_negative = int(
        np.count_nonzero(~predicted_foreground & ground_truth_foreground)
    )

    iou_denominator = true_positive + false_positive + false_negative
    precision_denominator = true_positive + false_positive
    recall_denominator = true_positive + false_negative

    iou = true_positive / iou_denominator if iou_denominator else 1.0
    precision = (
        true_positive / precision_denominator if precision_denominator else 0.0
    )
    recall = true_positive / recall_denominator if recall_denominator else 0.0
    f1 = (
        2.0 * precision * recall / (precision + recall)
        if precision + recall
        else 0.0
    )

    return BinaryMetrics(
        iou=float(iou),
        precision=float(precision),
        recall=float(recall),
        f1=float(f1),
    )
