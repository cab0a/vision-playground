"""Qualitative thresholding comparison for real images."""

from __future__ import annotations

import csv
from dataclasses import asdict, dataclass
from pathlib import Path

import cv2
import numpy as np

from vision_playground.thresholding import (
    apply_fixed_threshold,
    apply_otsu_threshold,
)

CSV_COLUMNS = (
    "filename",
    "method",
    "threshold",
    "foreground_fraction",
)


@dataclass(frozen=True, slots=True)
class RealImageRecord:
    """One thresholding result for a real image without ground truth."""

    filename: str
    method: str
    threshold: float
    foreground_fraction: float


def _fit_thumbnail(
    image: np.ndarray,
    width: int = 320,
    height: int = 220,
) -> np.ndarray:
    scale = min(width / image.shape[1], height / image.shape[0])
    resized = cv2.resize(
        image,
        (
            max(1, round(image.shape[1] * scale)),
            max(1, round(image.shape[0] * scale)),
        ),
        interpolation=cv2.INTER_AREA,
    )
    canvas = np.full((height, width), 24, dtype=np.uint8)
    y_offset = (height - resized.shape[0]) // 2
    x_offset = (width - resized.shape[1]) // 2
    canvas[
        y_offset : y_offset + resized.shape[0],
        x_offset : x_offset + resized.shape[1],
    ] = resized
    return canvas


def label_panel(image: np.ndarray, label: str) -> np.ndarray:
    """Fit an image to a labeled grayscale comparison panel."""
    thumbnail = _fit_thumbnail(image)
    panel = cv2.copyMakeBorder(
        thumbnail,
        38,
        0,
        0,
        0,
        cv2.BORDER_CONSTANT,
        value=24,
    )
    cv2.putText(
        panel,
        label,
        (8, 25),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.48,
        255,
        1,
        cv2.LINE_AA,
    )
    return panel


def _create_record(
    filename: str,
    method: str,
    threshold: float,
    mask: np.ndarray,
) -> RealImageRecord:
    return RealImageRecord(
        filename=filename,
        method=method,
        threshold=threshold,
        foreground_fraction=float(np.count_nonzero(mask) / mask.size),
    )


def _write_summary(records: list[RealImageRecord], output_path: Path) -> None:
    with output_path.open("w", encoding="utf-8", newline="") as output_file:
        writer = csv.DictWriter(
            output_file,
            fieldnames=CSV_COLUMNS,
            lineterminator="\n",
        )
        writer.writeheader()
        for record in records:
            row = asdict(record)
            row["threshold"] = f"{record.threshold:.2f}"
            row["foreground_fraction"] = f"{record.foreground_fraction:.6f}"
            writer.writerow(row)


def evaluate_real_images(
    image_paths: list[Path],
    output_dir: Path,
    fixed_threshold: int = 127,
) -> list[RealImageRecord]:
    """Apply both global methods and write a qualitative comparison."""
    if not image_paths:
        raise ValueError("At least one image is required.")

    output_dir.mkdir(parents=True, exist_ok=True)
    records: list[RealImageRecord] = []
    comparison_rows: list[np.ndarray] = []

    for image_path in sorted(image_paths):
        image = cv2.imread(str(image_path), cv2.IMREAD_GRAYSCALE)
        if image is None:
            raise OSError(f"Could not decode sample image: {image_path}")

        fixed_result = apply_fixed_threshold(image, threshold=fixed_threshold)
        otsu_result = apply_otsu_threshold(image)
        fixed_record = _create_record(
            image_path.name,
            fixed_result.method,
            fixed_result.threshold,
            fixed_result.mask,
        )
        otsu_record = _create_record(
            image_path.name,
            otsu_result.method,
            otsu_result.threshold,
            otsu_result.mask,
        )
        records.extend([fixed_record, otsu_record])

        comparison_rows.append(
            cv2.hconcat(
                [
                    label_panel(image, f"{image_path.name}: grayscale"),
                    label_panel(
                        fixed_result.mask,
                        (
                            f"fixed T={fixed_result.threshold:.0f}, "
                            f"fg={fixed_record.foreground_fraction:.2f}"
                        ),
                    ),
                    label_panel(
                        otsu_result.mask,
                        (
                            f"Otsu T={otsu_result.threshold:.0f}, "
                            f"fg={otsu_record.foreground_fraction:.2f}"
                        ),
                    ),
                ]
            )
        )

    _write_summary(records, output_dir / "thresholding_summary.csv")
    comparison_path = output_dir / "thresholding_comparison.jpg"
    if not cv2.imwrite(str(comparison_path), cv2.vconcat(comparison_rows)):
        raise OSError(f"Could not write comparison image: {comparison_path}")
    return records
