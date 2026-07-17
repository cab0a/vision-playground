"""Global thresholding methods used by the experiment."""

from __future__ import annotations

from dataclasses import dataclass

import cv2
import numpy as np


@dataclass(frozen=True, slots=True)
class ThresholdResult:
    """A binary prediction and the threshold used to create it."""

    method: str
    threshold: float
    mask: np.ndarray


def _validate_image(image: np.ndarray) -> None:
    if image.ndim != 2:
        raise ValueError("Thresholding requires a two-dimensional grayscale image.")
    if image.dtype != np.uint8:
        raise TypeError("Thresholding requires an unsigned 8-bit image.")


def apply_fixed_threshold(
    image: np.ndarray,
    threshold: int = 127,
) -> ThresholdResult:
    """Apply one fixed threshold to every pixel."""
    _validate_image(image)
    if not 0 <= threshold <= 255:
        raise ValueError("The fixed threshold must be between 0 and 255.")

    used_threshold, mask = cv2.threshold(
        image,
        threshold,
        255,
        cv2.THRESH_BINARY,
    )
    return ThresholdResult(
        method="fixed",
        threshold=float(used_threshold),
        mask=mask,
    )


def apply_otsu_threshold(image: np.ndarray) -> ThresholdResult:
    """Select and apply a global threshold using Otsu's method."""
    _validate_image(image)
    used_threshold, mask = cv2.threshold(
        image,
        0,
        255,
        cv2.THRESH_BINARY | cv2.THRESH_OTSU,
    )
    return ThresholdResult(
        method="otsu",
        threshold=float(used_threshold),
        mask=mask,
    )
