"""Controlled denoising experiments before Otsu thresholding."""

from __future__ import annotations

import csv
from dataclasses import asdict, dataclass
from pathlib import Path

import cv2
import numpy as np

from vision_playground.evaluation import calculate_binary_metrics
from vision_playground.real_images import label_panel
from vision_playground.synthetic import create_ground_truth
from vision_playground.thresholding import apply_otsu_threshold

DENOISING_METHODS = ("none", "gaussian", "median")
CSV_COLUMNS = (
    "noise_type",
    "denoising_method",
    "kernel_size",
    "otsu_threshold",
    "iou",
    "precision",
    "recall",
    "f1",
)


@dataclass(frozen=True, slots=True)
class DenoisingScenario:
    """One noisy synthetic image and its binary ground truth."""

    noise_type: str
    image: np.ndarray
    ground_truth: np.ndarray


@dataclass(frozen=True, slots=True)
class DenoisingRecord:
    """Metrics for one denoising method and noise condition."""

    noise_type: str
    denoising_method: str
    kernel_size: int | None
    otsu_threshold: float
    iou: float
    precision: float
    recall: float
    f1: float


def _validate_image(image: np.ndarray) -> None:
    if image.ndim != 2 or image.dtype != np.uint8:
        raise ValueError("Denoising requires a two-dimensional uint8 image.")


def _validate_kernel_size(kernel_size: int) -> None:
    if kernel_size < 3 or kernel_size % 2 == 0:
        raise ValueError("The kernel size must be an odd integer of at least 3.")


def add_gaussian_noise(
    image: np.ndarray,
    standard_deviation: float,
    rng: np.random.Generator,
) -> np.ndarray:
    """Add zero-mean Gaussian noise to a grayscale image."""
    _validate_image(image)
    if not np.isfinite(standard_deviation) or standard_deviation <= 0:
        raise ValueError("Gaussian standard deviation must be positive and finite.")
    noise = rng.normal(0.0, standard_deviation, image.shape)
    return np.clip(image.astype(np.float32) + noise, 0, 255).astype(np.uint8)


def add_salt_and_pepper_noise(
    image: np.ndarray,
    fraction: float,
    rng: np.random.Generator,
) -> np.ndarray:
    """Replace a fraction of pixels with equal amounts of black and white."""
    _validate_image(image)
    if not np.isfinite(fraction) or not 0 < fraction < 1:
        raise ValueError("Salt-and-pepper fraction must be between 0 and 1.")

    random_values = rng.random(image.shape)
    noisy = image.copy()
    half_fraction = fraction / 2.0
    noisy[random_values < half_fraction] = 0
    noisy[
        (random_values >= half_fraction) & (random_values < fraction)
    ] = 255
    return noisy


def apply_denoising(
    image: np.ndarray,
    method: str,
    kernel_size: int = 5,
) -> np.ndarray:
    """Apply one supported denoising method."""
    _validate_image(image)
    _validate_kernel_size(kernel_size)
    if method == "none":
        return image.copy()
    if method == "gaussian":
        return cv2.GaussianBlur(image, (kernel_size, kernel_size), 0)
    if method == "median":
        return cv2.medianBlur(image, kernel_size)
    raise ValueError(f"Unsupported denoising method: {method}")


def generate_denoising_scenarios(
    size: int = 256,
    seed: int = 17,
    gaussian_standard_deviation: float = 45.0,
    salt_and_pepper_fraction: float = 0.15,
) -> tuple[DenoisingScenario, ...]:
    """Generate comparable Gaussian and salt-and-pepper noise conditions."""
    ground_truth = create_ground_truth(size)
    clean_image = np.where(ground_truth != 0, 190, 55).astype(np.uint8)
    rng = np.random.default_rng(seed)
    gaussian_image = add_gaussian_noise(
        clean_image,
        gaussian_standard_deviation,
        rng,
    )
    salt_and_pepper_image = add_salt_and_pepper_noise(
        clean_image,
        salt_and_pepper_fraction,
        rng,
    )
    return (
        DenoisingScenario(
            "gaussian",
            gaussian_image,
            ground_truth.copy(),
        ),
        DenoisingScenario(
            "salt_and_pepper",
            salt_and_pepper_image,
            ground_truth.copy(),
        ),
    )


def _write_metrics(records: list[DenoisingRecord], output_path: Path) -> None:
    with output_path.open("w", encoding="utf-8", newline="") as output_file:
        writer = csv.DictWriter(
            output_file,
            fieldnames=CSV_COLUMNS,
            lineterminator="\n",
        )
        writer.writeheader()
        for record in records:
            row = asdict(record)
            row["kernel_size"] = (
                "" if record.kernel_size is None else record.kernel_size
            )
            row["otsu_threshold"] = f"{record.otsu_threshold:.2f}"
            for name in ("iou", "precision", "recall", "f1"):
                row[name] = f"{getattr(record, name):.6f}"
            writer.writerow(row)


def run_denoising_experiment(
    output_dir: Path,
    seed: int = 17,
    kernel_size: int = 5,
    gaussian_standard_deviation: float = 45.0,
    salt_and_pepper_fraction: float = 0.15,
) -> list[DenoisingRecord]:
    """Compare denoising methods and write reproducible artifacts."""
    _validate_kernel_size(kernel_size)
    output_dir.mkdir(parents=True, exist_ok=True)
    records: list[DenoisingRecord] = []
    comparison_rows: list[np.ndarray] = []

    for scenario in generate_denoising_scenarios(
        seed=seed,
        gaussian_standard_deviation=gaussian_standard_deviation,
        salt_and_pepper_fraction=salt_and_pepper_fraction,
    ):
        panels = [
            label_panel(scenario.image, f"{scenario.noise_type}: noisy input"),
            label_panel(scenario.ground_truth, "ground truth"),
        ]
        for method in DENOISING_METHODS:
            filtered_image = apply_denoising(
                scenario.image,
                method,
                kernel_size=kernel_size,
            )
            result = apply_otsu_threshold(filtered_image)
            metrics = calculate_binary_metrics(
                result.mask,
                scenario.ground_truth,
            )
            records.append(
                DenoisingRecord(
                    noise_type=scenario.noise_type,
                    denoising_method=method,
                    kernel_size=None if method == "none" else kernel_size,
                    otsu_threshold=result.threshold,
                    iou=metrics.iou,
                    precision=metrics.precision,
                    recall=metrics.recall,
                    f1=metrics.f1,
                )
            )
            panels.append(
                label_panel(
                    result.mask,
                    f"{method}: T={result.threshold:.0f}, IoU={metrics.iou:.3f}",
                )
            )
        comparison_rows.append(cv2.hconcat(panels))

    _write_metrics(records, output_dir / "denoising_metrics.csv")
    comparison_path = output_dir / "denoising_comparison.png"
    if not cv2.imwrite(str(comparison_path), cv2.vconcat(comparison_rows)):
        raise OSError(f"Could not write denoising comparison: {comparison_path}")
    return records
