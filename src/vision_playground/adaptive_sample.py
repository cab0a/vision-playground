"""Qualitative adaptive-threshold comparisons for public images."""

from __future__ import annotations

import csv
from collections.abc import Sequence
from dataclasses import asdict, dataclass
from pathlib import Path

import cv2
import numpy as np

from vision_playground.real_images import label_panel
from vision_playground.thresholding import apply_adaptive_threshold

CSV_COLUMNS = (
    "filename",
    "configuration",
    "block_size",
    "constant_c",
    "foreground_fraction",
)


@dataclass(frozen=True, slots=True)
class AdaptiveConfiguration:
    """One named adaptive-threshold parameter configuration."""

    name: str
    block_size: int
    constant_c: float


@dataclass(frozen=True, slots=True)
class AdaptiveSampleRecord:
    """One adaptive result for a real image without ground truth."""

    filename: str
    configuration: str
    block_size: int
    constant_c: float
    foreground_fraction: float


DEFAULT_CONFIGURATIONS = (
    AdaptiveConfiguration("small_block", 31, -10.0),
    AdaptiveConfiguration("reference", 127, -10.0),
    AdaptiveConfiguration("large_block", 191, -10.0),
    AdaptiveConfiguration("positive_c", 127, 5.0),
)


def _write_summary(
    records: list[AdaptiveSampleRecord],
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
            row["constant_c"] = f"{record.constant_c:.2f}"
            row["foreground_fraction"] = f"{record.foreground_fraction:.6f}"
            writer.writerow(row)


def evaluate_adaptive_samples(
    image_paths: list[Path],
    output_dir: Path,
    configurations: Sequence[
        AdaptiveConfiguration
    ] = DEFAULT_CONFIGURATIONS,
) -> list[AdaptiveSampleRecord]:
    """Apply adaptive configurations and write a qualitative comparison."""
    if not image_paths:
        raise ValueError("At least one image is required.")
    if not configurations:
        raise ValueError("At least one adaptive configuration is required.")

    output_dir.mkdir(parents=True, exist_ok=True)
    records: list[AdaptiveSampleRecord] = []
    comparison_rows: list[np.ndarray] = []

    for image_path in sorted(image_paths):
        image = cv2.imread(str(image_path), cv2.IMREAD_GRAYSCALE)
        if image is None:
            raise OSError(f"Could not decode sample image: {image_path}")

        panels = [label_panel(image, f"{image_path.name}: grayscale")]
        for configuration in configurations:
            result = apply_adaptive_threshold(
                image,
                block_size=configuration.block_size,
                constant_c=configuration.constant_c,
            )
            foreground_fraction = float(
                np.count_nonzero(result.mask) / result.mask.size
            )
            records.append(
                AdaptiveSampleRecord(
                    filename=image_path.name,
                    configuration=configuration.name,
                    block_size=configuration.block_size,
                    constant_c=configuration.constant_c,
                    foreground_fraction=foreground_fraction,
                )
            )
            panels.append(
                label_panel(
                    result.mask,
                    (
                        f"{configuration.name}: b={configuration.block_size}, "
                        f"C={configuration.constant_c:g}, "
                        f"fg={foreground_fraction:.2f}"
                    ),
                )
            )
        comparison_rows.append(cv2.hconcat(panels))

    _write_summary(records, output_dir / "adaptive_parameter_summary.csv")
    comparison_path = output_dir / "adaptive_parameter_comparison.jpg"
    if not cv2.imwrite(str(comparison_path), cv2.vconcat(comparison_rows)):
        raise OSError(f"Could not write comparison image: {comparison_path}")
    return records
