"""Thresholding methods used by the experiment."""

from __future__ import annotations

from dataclasses import dataclass

import cv2
import numpy as np


@dataclass(frozen=True, slots=True)
class ThresholdResult:
    """A binary prediction and the parameters used to create it."""

    method: str
    threshold: float | None
    mask: np.ndarray
    block_size: int | None = None
    constant_c: float | None = None


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


def apply_adaptive_threshold(
    image: np.ndarray,
    block_size: int = 127,
    constant_c: float = -10.0,
) -> ThresholdResult:
    """Apply Gaussian-weighted adaptive thresholding."""
    _validate_image(image)
    if block_size < 3 or block_size % 2 == 0:
        raise ValueError("The adaptive block size must be an odd integer of at least 3.")
    if not np.isfinite(constant_c):
        raise ValueError("The adaptive constant must be finite.")

    mask = cv2.adaptiveThreshold(
        image,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        block_size,
        constant_c,
    )
    return ThresholdResult(
        method="adaptive",
        threshold=None,
        mask=mask,
        block_size=block_size,
        constant_c=float(constant_c),
    )
