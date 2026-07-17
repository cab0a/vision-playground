"""Canny edge stability checks on freely reusable photographs."""

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
from vision_playground.edge_detection import (
    apply_canny,
    calculate_edge_metrics,
)
from vision_playground.real_images import label_panel

CSV_COLUMNS = (
    "filename",
    "noise_type",
    "denoising_method",
    "kernel_size",
    "low_threshold",
    "high_threshold",
    "tolerance_pixels",
    "edge_pixels",
    "reference_edge_f1",
    "precision",
    "recall",
)


@dataclass(frozen=True, slots=True)
class EdgeSampleRecord:
    """One noisy-image edge map compared with a clean Canny reference."""

    filename: str
    noise_type: str
    denoising_method: str
    kernel_size: int | None
    low_threshold: int
    high_threshold: int
    tolerance_pixels: int
    edge_pixels: int
    reference_edge_f1: float
    precision: float
    recall: float


def _write_summary(
    records: list[EdgeSampleRecord],
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
            for name in ("reference_edge_f1", "precision", "recall"):
                row[name] = f"{getattr(record, name):.6f}"
            writer.writerow(row)


def evaluate_edge_samples(
    image_paths: list[Path],
    output_dir: Path,
    seed: int = 41,
    kernel_size: int = 5,
    low_threshold: int = 125,
    high_threshold: int = 250,
    tolerance_pixels: int = 2,
    gaussian_standard_deviation: float = 45.0,
    salt_and_pepper_fraction: float = 0.15,
) -> list[EdgeSampleRecord]:
    """Measure Canny stability after controlled noise and denoising."""
    if not image_paths:
        raise ValueError("At least one image is required.")

    output_dir.mkdir(parents=True, exist_ok=True)
    records: list[EdgeSampleRecord] = []
    comparison_rows: list[np.ndarray] = []

    for image_index, image_path in enumerate(sorted(image_paths)):
        image = cv2.imread(str(image_path), cv2.IMREAD_GRAYSCALE)
        if image is None:
            raise OSError(f"Could not decode sample image: {image_path}")
        reference_edges = apply_canny(
            image,
            low_threshold,
            high_threshold,
        )

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
                label_panel(reference_edges, "clean Canny reference"),
            ]
            for method in DENOISING_METHODS:
                filtered_image = apply_denoising(
                    noisy_image,
                    method,
                    kernel_size=kernel_size,
                )
                edges = apply_canny(
                    filtered_image,
                    low_threshold,
                    high_threshold,
                )
                metrics = calculate_edge_metrics(
                    edges,
                    reference_edges,
                    tolerance_pixels=tolerance_pixels,
                )
                records.append(
                    EdgeSampleRecord(
                        filename=image_path.name,
                        noise_type=noise_type,
                        denoising_method=method,
                        kernel_size=None if method == "none" else kernel_size,
                        low_threshold=low_threshold,
                        high_threshold=high_threshold,
                        tolerance_pixels=tolerance_pixels,
                        edge_pixels=int(np.count_nonzero(edges)),
                        reference_edge_f1=metrics.f1,
                        precision=metrics.precision,
                        recall=metrics.recall,
                    )
                )
                panels.append(
                    label_panel(
                        edges,
                        f"{method}: reference F1={metrics.f1:.3f}",
                    )
                )
            comparison_rows.append(cv2.hconcat(panels))

    _write_summary(records, output_dir / "edge_detection_summary.csv")
    comparison_path = output_dir / "edge_detection_comparison.jpg"
    if not cv2.imwrite(str(comparison_path), cv2.vconcat(comparison_rows)):
        raise OSError(f"Could not write edge sample: {comparison_path}")
    return records
