"""Denoising stability checks on freely reusable photographs."""

from __future__ import annotations

import csv
from dataclasses import asdict, dataclass
from pathlib import Path

import cv2
import numpy as np

from vision_playground.denoising import (
    DENOISING_METHODS,
    add_gaussian_noise,
    add_salt_and_pepper_noise,
    apply_denoising,
)
from vision_playground.evaluation import calculate_binary_metrics
from vision_playground.real_images import label_panel
from vision_playground.thresholding import apply_otsu_threshold

CSV_COLUMNS = (
    "filename",
    "noise_type",
    "denoising_method",
    "kernel_size",
    "otsu_threshold",
    "reference_mask_iou",
    "foreground_fraction",
)


@dataclass(frozen=True, slots=True)
class DenoisingSampleRecord:
    """One noisy-image result compared with a clean Otsu reference mask."""

    filename: str
    noise_type: str
    denoising_method: str
    kernel_size: int | None
    otsu_threshold: float
    reference_mask_iou: float
    foreground_fraction: float


def _write_summary(
    records: list[DenoisingSampleRecord],
    output_path: Path,
) -> None:
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
            row["reference_mask_iou"] = f"{record.reference_mask_iou:.6f}"
            row["foreground_fraction"] = f"{record.foreground_fraction:.6f}"
            writer.writerow(row)


def evaluate_denoising_samples(
    image_paths: list[Path],
    output_dir: Path,
    seed: int = 29,
    kernel_size: int = 5,
    gaussian_standard_deviation: float = 45.0,
    salt_and_pepper_fraction: float = 0.15,
) -> list[DenoisingSampleRecord]:
    """Measure Otsu-mask stability after controlled noise and denoising."""
    if not image_paths:
        raise ValueError("At least one image is required.")

    output_dir.mkdir(parents=True, exist_ok=True)
    records: list[DenoisingSampleRecord] = []
    comparison_rows: list[np.ndarray] = []

    for image_index, image_path in enumerate(sorted(image_paths)):
        image = cv2.imread(str(image_path), cv2.IMREAD_GRAYSCALE)
        if image is None:
            raise OSError(f"Could not decode sample image: {image_path}")
        reference_mask = apply_otsu_threshold(image).mask

        for noise_index, noise_type in enumerate(
            ("gaussian", "salt_and_pepper")
        ):
            rng = np.random.default_rng(seed + image_index * 10 + noise_index)
            if noise_type == "gaussian":
                noisy_image = add_gaussian_noise(
                    image,
                    gaussian_standard_deviation,
                    rng,
                )
            else:
                noisy_image = add_salt_and_pepper_noise(
                    image,
                    salt_and_pepper_fraction,
                    rng,
                )

            panels = [
                label_panel(
                    noisy_image,
                    f"{image_path.name}: {noise_type}",
                ),
                label_panel(reference_mask, "clean Otsu reference"),
            ]
            for method in DENOISING_METHODS:
                filtered_image = apply_denoising(
                    noisy_image,
                    method,
                    kernel_size=kernel_size,
                )
                result = apply_otsu_threshold(filtered_image)
                metrics = calculate_binary_metrics(
                    result.mask,
                    reference_mask,
                )
                foreground_fraction = float(
                    np.count_nonzero(result.mask) / result.mask.size
                )
                records.append(
                    DenoisingSampleRecord(
                        filename=image_path.name,
                        noise_type=noise_type,
                        denoising_method=method,
                        kernel_size=None if method == "none" else kernel_size,
                        otsu_threshold=result.threshold,
                        reference_mask_iou=metrics.iou,
                        foreground_fraction=foreground_fraction,
                    )
                )
                panels.append(
                    label_panel(
                        result.mask,
                        f"{method}: reference IoU={metrics.iou:.3f}",
                    )
                )
            comparison_rows.append(cv2.hconcat(panels))

    _write_summary(records, output_dir / "denoising_summary.csv")
    comparison_path = output_dir / "denoising_comparison.jpg"
    if not cv2.imwrite(str(comparison_path), cv2.vconcat(comparison_rows)):
        raise OSError(f"Could not write denoising sample: {comparison_path}")
    return records
