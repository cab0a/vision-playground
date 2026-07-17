"""Deterministic synthetic images for thresholding evaluation."""

from __future__ import annotations

from dataclasses import dataclass

import cv2
import numpy as np


@dataclass(frozen=True, slots=True)
class SyntheticScenario:
    """One generated grayscale image and its binary ground truth."""

    name: str
    image: np.ndarray
    ground_truth: np.ndarray


def create_ground_truth(size: int = 256) -> np.ndarray:
    """Create a binary mask containing several geometric shapes."""
    if size < 128:
        raise ValueError("Image size must be at least 128 pixels.")

    scale = size / 256.0
    mask = np.zeros((size, size), dtype=np.uint8)

    cv2.rectangle(
        mask,
        (round(20 * scale), round(25 * scale)),
        (round(108 * scale), round(118 * scale)),
        255,
        thickness=-1,
    )
    cv2.circle(
        mask,
        (round(180 * scale), round(72 * scale)),
        round(39 * scale),
        255,
        thickness=-1,
    )
    triangle = np.array(
        [
            [round(72 * scale), round(218 * scale)],
            [round(132 * scale), round(142 * scale)],
            [round(196 * scale), round(218 * scale)],
        ],
        dtype=np.int32,
    )
    cv2.fillPoly(mask, [triangle], 255)
    return mask


def _render_levels(
    ground_truth: np.ndarray,
    background: float,
    foreground: float,
    noise_std: float,
    rng: np.random.Generator,
) -> np.ndarray:
    foreground_mask = ground_truth != 0
    image = np.where(foreground_mask, foreground, background).astype(np.float32)
    if noise_std:
        image += rng.normal(0.0, noise_std, image.shape).astype(np.float32)
    return np.clip(image, 0, 255).astype(np.uint8)


def generate_scenarios(
    size: int = 256,
    seed: int = 7,
) -> tuple[SyntheticScenario, ...]:
    """Generate controlled contrast, noise, and illumination conditions."""
    ground_truth = create_ground_truth(size)
    foreground_mask = ground_truth != 0
    rng = np.random.default_rng(seed)

    uniform_clean = _render_levels(
        ground_truth,
        background=45,
        foreground=205,
        noise_std=0,
        rng=rng,
    )
    shifted_low_contrast = _render_levels(
        ground_truth,
        background=135,
        foreground=175,
        noise_std=10,
        rng=rng,
    )

    illumination = np.tile(
        np.linspace(35, 165, size, dtype=np.float32),
        (size, 1),
    )
    uneven_illumination = illumination + foreground_mask.astype(np.float32) * 70
    uneven_illumination += rng.normal(0.0, 5.0, illumination.shape).astype(
        np.float32
    )
    uneven_illumination = np.clip(uneven_illumination, 0, 255).astype(np.uint8)

    high_noise = _render_levels(
        ground_truth,
        background=55,
        foreground=185,
        noise_std=30,
        rng=rng,
    )

    return (
        SyntheticScenario("uniform_clean", uniform_clean, ground_truth.copy()),
        SyntheticScenario(
            "shifted_low_contrast",
            shifted_low_contrast,
            ground_truth.copy(),
        ),
        SyntheticScenario(
            "uneven_illumination",
            uneven_illumination,
            ground_truth.copy(),
        ),
        SyntheticScenario("high_noise", high_noise, ground_truth.copy()),
    )
